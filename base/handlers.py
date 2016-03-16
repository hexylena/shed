import hashlib
import os
import shutil
import tarfile
import tempfile
import xml.etree.ElementTree as ET
import yaml
from .models import Version, Installable, SuiteVersion
from archive import safemembers
from distutils.version import LooseVersion
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from galaxy.tools.loader_directory import load_tool_elements_from_path
from galaxy.util.xml_macros import load
from planemo import shed

import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

def unpack_tarball(tarball_path):
    """
    Unpack a tarball into a temporary directory
    """
    temp = tempfile.mkdtemp(prefix='shed.tmp.')
    ar = tarfile.open(tarball_path)
    logging.debug("Unpacking %s to %s", tarball_path, temp)
    ar.extractall(path=temp, members=safemembers(ar))
    ar.close()
    return temp


class ToolContext():
    def __init__(self, tool_xml_path):
        self.tool_xml_path = tool_xml_path

    def __enter__(self):
        return load(self.tool_xml_path).getroot()

    def __exit__(self, *args, **kwargs):
        pass


class ToolHandler():

    def __init__(self, installable, tarball, sha256sum):
        self.installable = installable
        self.tarball = tarball
        self._assertUploadIntegrity(tarball, sha256sum)
        self.tarball_contents = unpack_tarball(tarball)

    def _assertSemVerIncrease(self, tool_version):
        # Assert that this is the largest version number we've ever seen.
        for previous_version in self.installable.version_set.all():
            if semver.compare(tool_version, previous_version.version) != 1:
                raise Exception("Decrease in version number")

    def _assertNewVersion(self, tool_version):
        # Necessary? LooseVersion doesn't error even on crap like 'asdf'
        lv = LooseVersion(tool_version).vstring
        for previous_version in self.installable.version_set.all():
            if lv == previous_version.version:
                raise Exception("Duplicate Version")

    def _assertUploadIntegrity(self, archive_path, expected_sha256):
        # http://stackoverflow.com/a/4213255
        if expected_sha256 is None:
            log.warn("No sha256sum provided")
            return

        m = hashlib.sha256()
        with open(archive_path, 'rb') as f:
            for chunk in iter(lambda: f.read(128 * m.block_size), b''):
                m.update(chunk)
        assert m.hexdigest() == expected_sha256, 'Tarball has incorrect hash'

    def demultiplex(self):
        tools = load_tool_elements_from_path(self.tarball_contents)
        # Only one tool file is allowed per archive, per spec
        if len(tools) > 1:
            # We'll take advantage of planemo to handle the demultiplexing for
            # us.
            # with open(os.path.join(self.tarball_contents, '.shed.yml'), 'w') as handle:
                # data = self.installable.shed_yaml()
                # data.update({
                    # 'auto_tool_repositories': {
                        # 'name_template':'{{ tool_id }}',
                        # 'description_template': 'Auto demultiplexed {{ tool_name }}',
                    # },
                    # 'suite': {
                        # 'name': data['name'],
                        # 'description': data['description']
                    # }
                # })
                # del data['name']
                # del data['description']
                # handle.write(yaml.dumps({
                    # 'owner': self.installable.owner.username,
                    # 'remote_repository_url': self.installable.remote_repository_url,
                # })

            # print self.tarball
            # print os.path.exists(self.tarball_contents + '/.shed.yml')
            # print os.listdir(self.tarball_contents)
            raise Exception("Too many tools")
        elif len(tools) == 1:
            yield (tools[0][0], 'tool')
        elif len(tools) == 0:
            # No tools found, maybe it is something else?
            files = os.listdir(self.tarball_contents)
            if len(files) == 1 and 'repository_dependencies.xml' in files[0]:
                yield (
                    os.path.join(self.tarball_contents, files[0]),
                    'suite'
                )

    def getDependencies(self, tool_root):
        reqs = []
        for node in tool_root.findall('requirements/requirement'):
            x = node.attrib
            x['requirement'] = node.text
            reqs.append(x)
        return reqs

    def generate_version_from_tool(self, tool_root, **kwargs):
        version = tool_root.attrib['version']
        # Duplicate assertion, probably unnecessary, but I was lazy in
        # writing tests and hit this case, so someone else might too.
        self._assertNewVersion(version)

        version = Version(
            version=version,
            uploaded=timezone.now(),
            installable=self.installable,
            **kwargs
        )
        version.save()
        return version

    def persist_archive(self, archive_path, version):
        installable = version.installable
        owner = installable.owner
        package_dir = os.path.join(
            settings.STORAGE_AREA,
            owner.username,
            installable.name,
        )

        if not os.path.exists(package_dir):
            os.makedirs(package_dir)

        path = os.path.join(package_dir, version.version)
        # TODO: hardcoded extension
        shutil.move(archive_path, path + '.tar.gz')

        extracted = unpack_tarball(path + '.tar.gz')
        shutil.move(extracted, path)


def _process_tool(th, user, file, installable, commit, sha=None, sig=None):
    with ToolContext(file) as tool_root:
        version = th.generate_version_from_tool(
            tool_root,
            commit_message=commit,
            tar_gz_sig_available=sig is not None
        )
        return version

def _process_suite(th, user, file, installable, commit, sha=None, sig=None):
    tree = ET.parse(file)
    root = tree.getroot()

    repos = root.findall('repository')
    versions = []
    for repo in repos:
        # The .get() require exactly one object is returned
        user = User.objects.get(username=repo.attrib['owner'])
        contained_installable = Installable.objects.filter(owner=user).get(name=repo.attrib['name'])
        if 'version' in repo.attrib:
            version = Version.objects.filter(installable=contained_installable).get(version=repo.attrib['version'])
            versions.append(version)
        else:
            # Don't really know what they expected to happen, lol
            versions.append(contained_installable.latest_version)

    # Ensure uniqueness?
    suite_version = root.attrib.get('version', '1.0.0')

    related_versions = SuiteVersion.objects.filter(installable=installable).filter(version=suite_version).all()
    if len(related_versions) != 0:
        raise Exception("Suite of version " + suite_version + " already exists")

    sv = SuiteVersion(
        version=suite_version,
        commit_message=commit,
        installable=installable,
    )
    sv.save()

    # We don't need to check uniqueness here because we've forced it above with
    # the requirement that sv always be a new object.
    for v in versions:
        sv.contained_versions.add(v)
    sv.save()
    return sv

def process_tarball(user, tarball, installable, commit, sha=None, sig=None):
    assert installable.is_editable_by(user), 'Access Denied'

    th = ToolHandler(installable, tarball, sha)
    log.debug('inst: %s', installable)

    retdata = []
    for (demultiplexed_repo, dmr_repo_type) in th.demultiplex():
        log.debug('[%s] %s', dmr_repo_type, demultiplexed_repo)

        if dmr_repo_type == 'tool':
            ret = _process_tool(th, user, demultiplexed_repo, installable, commit, sha=sha, sig=sig)
        elif dmr_repo_type == 'suite':
            ret = _process_suite(th, user, demultiplexed_repo, installable, commit, sha=sha, sig=sig)
        else:
            raise Exception("Unhandled repository type")

        # TODO: there's another archive around here that needs to be cleaned.
        th.persist_archive(tarball, ret)
        retdata.append(ret)
        log.debug("processed: %s", ret)

    return retdata
