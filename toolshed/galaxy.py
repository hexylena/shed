import tarfile


def locate_version_number(archive_path):
    """
    Dummy locate version number function which just reads the value from a file
    name VERSION.

    TODO: A real version of this function will read the tool_dependencies.xml
    or tool.xml file, render it, grab the version #, and use that.
    """
    print 'Locating version # from %s' % archive_path
    tar = tarfile.open(archive_path)
    for member in tar.getmembers():
        if member.name == 'VERSION':
            f = tar.extractfile(member)
            version = f.read().strip()
            return version

    raise Exception("Could not locate version number")
