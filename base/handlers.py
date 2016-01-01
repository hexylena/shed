import os
import shutil
import tempfile
import tarfile
import hashlib
from .models import Version, Installable
from galaxy.tools.loader_directory import load_tool_elements_from_path
from galaxy.util.xml_macros import load
from django.utils import timezone
from archive import safemembers
from distutils.version import LooseVersion

import logging
logging.basicConfig(level=logging.INFO)
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

    def __init__(self, installable):
        self.installable = installable

    def _assertSemVerIncrease(self, tool_version):
        # Assert that this is the largest version number we've ever seen.
        for previous_version in self.installable.version_set.all():
            if semver.compare(tool_version, previous_version.version) != 1:
                raise Exception("Decrease in version number")

    def _assertNewVersion(self, tool_version):
        # Necessary? LooseVersino doesn't error even on crap like 'asdf'
        lv = LooseVersion(tool_version).vstring
        for previous_version in self.installable.version_set.all():
            if lv == previous_version.version:
                raise Exception("Duplicate Version")

    def _assertUploadIntegrity(self, archive_path, expected_sha256):
        # http://stackoverflow.com/a/4213255
        m = hashlib.sha256()
        with open(archive_path, 'rb') as f:
            for chunk in iter(lambda: f.read(128 * m.block_size), b''):
                m.update(chunk)
        assert m.hexdigest() == expected_sha256, 'Tarball has incorrect hash'

    def getDependencies(self, tool_root):
        reqs = []
        for node in tool_root.findall('requirements/requirement'):
            x = node.attrib
            x['requirement'] = node.text
            reqs.append(x)
        return reqs

    def validate_archive(self, tarball_path, sha256sum):
        """Ensure that an uploaded archive is valid by all metrics
        """
        self._assertUploadIntegrity(tarball_path, sha256sum)

        contents = unpack_tarball(tarball_path)
        tools = load_tool_elements_from_path(contents)
        # Only one tool file is allowed per archive, per spec
        assert len(tools) == 1, 'Too many tools found'
        tool = tools[0]

        with ToolContext(tool[0]) as tool_root:
            tool_attrib = tool_root.attrib
            self._assertNewVersion(tool_attrib['version'])

        return tool

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


class ValidatedArchive():
    """
    Simple context manager for dealing with tarballs

    with ValidatedArchive(InstallableX, my.tar.gz) as unpacked_dir:
        # do something with the directory

    """
    def __init__(self, installable, archive):
        self.installable = installable
        self.ar = archive

    def __enter__(self):
        self.unpacked_directory = validate_installable_archive(self.installable, self.ar)
        return self.unpacked_directory

    def __exit__(self):
        shutil.rmtree(self.unpacked_directory)


def process_tarball(user, file, installable, commit, sha, sig=None):
    assert installable.can_edit(user), 'Access Denied'

    th = ToolHandler(installable)
    tool = th.validate_archive(file, sha)

    with ToolContext(tool[0]) as tool_root:
        version = th.generate_version_from_tool(
            tool,
            commit=commit,
            tar_gz_sig_available=sig is not None
        )
