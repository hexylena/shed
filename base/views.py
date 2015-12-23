import datetime
import os
import shutil
import tempfile
from sendfile import sendfile
from .models import Revision, Installable
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from hashlib import sha256
from django.conf import settings
from django import forms
from django.http import HttpResponse

import logging
log = logging.getLogger(__name__)


def api_list(request):
    apis = {
        'title': 'API Index',
        'comment': 'Completely nonstandard API index listing. TODO',
        'apis': [
            {
                'name': 'planemo',
                'description': 'An API compatible with what Galaxyproject\'s planemo currently uses for a toolshed mockup during testing',
                'url': '/api/planemo/v1/',
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
        # TODO: embed revision #
    }
    return JsonResponse(apis, json_dumps_params={'indent': 2})


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
    for revision in installable.revision_set.all():
        data += """<li><a href="%s/%s">%s</a> - %s</li>""" % \
            (name, revision.id, revision.version, revision.tar_gz_sha256)
        if revision.tar_gz_sig_available:
            data += '<li><a href="' + name + '/' + str(revision.id) \
                + '.asc">' + revision.version + '.asc</a></li>'
            print revision.version[0]
    return HttpResponse("<html><head></head><body><h1>" + installable.name + "</h1><ul>" + data + "</ul></body></html>")


def download_file(request, name=None, path=None):
    if name is None or path is None:
        return HttpResponse(status=404)
    pk = path.split('.asc')[0]

    installable = Installable.objects.get(pk=name)
    revision = Revision.objects \
        .filter(installable=installable).get(pk=pk)

    (directory, c) = get_folder(revision.tar_gz_sha256)

    dl_file_name = '%s-%s.tar.gz' % (installable.name, revision.version)
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


class UploadFileForm(forms.Form):
    installable_id = forms.IntegerField()
    file = forms.FileField()
    sig = forms.CharField()
    commit = forms.CharField()


def get_folder(uuid):
    (a, b, c) = uuid[0:2], uuid[2:4], uuid[4:]
    directory = os.path.join(settings.TOOLSHED_UPLOAD_PATH, a, b)
    if not os.path.exists(directory):
        os.makedirs(directory)

    return directory, c


def get_version(path):
    return '1.0.0'


def persist_to_tempfile(fileobj):
    temp_upload = tempfile.NamedTemporaryFile(prefix='ts.upload.', delete=False)
    m = sha256()
    for chunk in fileobj.chunks():
        temp_upload.write(chunk)
        m.update(chunk)

    temp_upload.close()
    return temp_upload.name, m.hexdigest()


# We're making a complexity exception here as uploading is an error prone
# process, and we want to both fail whenever we can, and fail nicely, which
# involves some extraneous try/catching
@csrf_exempt
def register(request, *args, **kwargs):
    # If they've sent a bad token, we'll fail here

    auth_data = {}
    # Otherwise, it's a valid user.
    user = User.objects.get(pk=auth_data['user_id'])

    # Actually parse what they sent
    form = UploadFileForm(request.POST, request.FILES)
    if form.is_valid():
        # lots of things we try and fail asap
        installable_id = form.data['installable_id']
        installable = Installable.objects.get(pk=installable_id)
        if not installable.can_edit(user):
            raise Exception("User not allow to edit this installable")

        has_sig = len(form.data['sig']) > 0

        tmp_path, sha256 = persist_to_tempfile(request.FILES['file'])

        rev_kwargs = {
            'commit_message': form.data['commit'],
            'uploaded': datetime.datetime.utcnow(),
            'tar_gz_sha256': sha256,
            'tar_gz_sig_available': has_sig,
            'installable': installable,
            'replacement_revision': None,
            'downloads': 0,
        }

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

        conflicting_version = Revision.objects \
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
                handle.write(form.data['sig'])

        r = Revision(**rev_kwargs)
        r.save()
