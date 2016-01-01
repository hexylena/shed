import os
import shutil
import tempfile
import tarfile
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

    def validate_archive(self, tarball_path):
        """
        """
        contents = unpack_tarball(tarball_path)
        tools = load_tool_elements_from_path(contents)
        # Only one tool file is allowed per archive, per spec
        assert len(tools) == 1
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

def validate_package(user, file, installable_id, commit, sig):
    try:
        # Try to get the version from their file
        rev_kwargs['version'] = get_version(tmp_path)
    except Exception, e:
        # Otherwise cancel everything and quit ASAP
        try:
            os.unlink(tmp_path)
        except Exception, e:
            log.error(e)
            return JsonResponse({'error': True, 'message': 'Server Error'})

    conflicting_version = Version.objects \
        .filter(installable=installable) \
        .filter(version=rev_kwargs['version']).all()
    if len(conflicting_version) > 0:
        return JsonResponse({'error': True, 'message': 'Duplicate Version'})

    # If they've made it this far, they're doing pretty good
    (final_dir, final_fn) = get_folder(rev_kwargs['tar_gz_sha256'])
    final_data_path = os.path.join(final_dir, final_fn)

    shutil.move(tmp_path, final_data_path)

    if has_sig:
        with open(final_data_path + '.asc', 'w') as handle:
            handle.write(sig)

    r = Version(**rev_kwargs)
    r.save()

    return r
