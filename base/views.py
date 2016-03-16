import os
from sendfile import sendfile
from .models import Version, Installable
from django.http import JsonResponse
from django.http import HttpResponse

import logging
log = logging.getLogger(__name__)


def api_list(request):
    apis = {
        'title': 'API Index',
        'comment': 'Completely nonstandard API index listing. TODO',
        'apis': [
            {
                'name': 'galaxy',
                'description': 'An API for Galaxy\'s newest iteration of planemo and shedclient-beta',
                'url': '/api/galaxy/v1/',
                'version': '1',
                'available': True,
            },
            {
                'name': 'toolshed_legacy',
                'description': 'An API compatible with what Galaxyproject\'s planemo currently uses for a toolshed mockup during testing',
                'url': '/api/toolshed_legacy/v1/',
                'version': '1',
                'available': True,
            },
            {
                'name': 'drf',
                'description': 'An API built for the original Toolshed v2.0, now unused',
                'url': '/api/drf/',
                'version': '1',
                'available': True,
            },
            # {
                # 'name': 'cwl',
                # 'description': 'An API based on the CWL spec',
                # 'available': False,
            # }
        ],
        'LICENSE': 'AGPLv3',
        'codebase': 'https://github.com/erasche/shed',
        # TODO: embed version #
    }
    response = JsonResponse(apis, json_dumps_params={'indent': 2}, status=404)


def list_uploads(request):
    # TODO: replace with a proper/nice template
    template = "<html><head></head><body><ul>%s</ul></body></html>"
    data = Installable.objects.order_by('name').all()
    parsed_data = ['<li><a href="uploads/' + str(x.id) + '">' + x.name + '</a></li>' for x in data]
    return HttpResponse(template % ('\n'.join(parsed_data)))


def list_upload_folder(request, name=None):
    if name is None:
        return HttpResponse(status=404)

    # TODO: replace with a proper/nice template
    installable = Installable.objects.get(pk=name)
    data = ""
    for version in installable.version_set.all():
        data += """<li><a href="%s/%s">%s</a> - %s</li>""" % \
            (name, version.id, version.version, version.tar_gz_sha256)
        if version.tar_gz_sig_available:
            data += '<li><a href="' + name + '/' + str(version.id) \
                + '.asc">' + version.version + '.asc</a></li>'
            print version.version[0]
    return HttpResponse("<html><head></head><body><h1>" + installable.name + "</h1><ul>" + data + "</ul></body></html>")


def download_file(request, name=None, path=None):
    if name is None or path is None:
        return HttpResponse(status=404)
    pk = path.split('.asc')[0]

    installable = Installable.objects.get(pk=name)
    version = Version.objects \
        .filter(installable=installable).get(pk=pk)

    # (directory, c) = get_folder(version.tar_gz_sha256)
    directory, c = None

    dl_file_name = '%s-%s.tar.gz' % (installable.name, version.version)
    on_disk_path = os.path.join(directory, c)
    if path.endswith('.asc'):
        on_disk_path += '.asc'
        dl_file_name += '.asc'

    return sendfile(
        request,
        on_disk_path,
        attachment=True,
        attachment_filename=dl_file_name
    )
