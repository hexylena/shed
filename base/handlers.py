import os
import shutil
import tempfile
import tarfile
# from .models import Version, Installable
from galaxy.tools.loader_directory import load_tool_elements_from_path
from archive import safemembers

import logging
log = logging.getLogger(__name__)

def validate_tarball(tarball):
    pass


def unpack_tarball(tarball_path):
    """
    Unpack a tarball into a temporary directory
    """
    temp = tempfile.mkdtemp()
    ar = tarfile.open(tarball_path)
    logging.debug("Unpacking %s to %s", tarball_path, temp)
    ar.extractall(path=temp, members=safemembers(ar))
    ar.close()
    return temp

def validate_installable_archive(installable, tarball_path):
    """
    """
    contents = unpack_tarball(tarball_path)
    tools = load_tool_elements_from_path(contents)
    assert len(tools) == 1
    return tools


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
