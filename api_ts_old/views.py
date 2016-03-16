import json
import os
import base64
import tempfile
from api_drf.serializer import InstallableSerializer, VersionSerializer, SuiteVersionSerializer
from django.http import JsonResponse
from base.models import Installable, UserExtension, Tag, Version, SuiteVersion
from base.handlers import process_tarball
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django import forms


class UploadFileForm(forms.Form):
    commit_message = forms.CharField()
    file = forms.FileField()
    key = forms.CharField()


def user_or_none(request):
    key = request.GET.get('key', None)
    if key is None:
        # Try post
        key = request.POST.get('key', None)

        if key is None:
            return None


    try:
        user = UserExtension.objects.get(api_key=key)
        return user
    except UserExtension.DoesNotExist:
        return None

# Create your views here.
def v1_index(request):
    return JsonResponse({
        'routes': {
            'users': {
                'url': reverse('api-planemo-user-list'),
            },
            'categories': {
                'url': reverse('api-planemo-cat-list'),
            },
            'repositories': {
                'url': reverse('api-planemo-repo-list'),
            }
        }
    }, json_dumps_params={'indent': 2})


@csrf_exempt
def v1_repo_list(request):
    if request.GET.get('q', None) is not None:
        return v1_search(request)

    if request.method == 'POST':
        user_extension = user_or_none(request)
        if user_extension is None:
            return HttpResponse('Unauthorized', status=401)
        # Read in data
        data = json.loads(request.body)

        tags = [get_object_or_404(Tag, pk=x) for x in data['category_ids[]']]
        # Find other possible installable
        alt_installables = Installable.objects.filter(name=data['name']).all()
        alt_installables = [i for i in alt_installables if i.can_edit(user_extension.user)]
        if len(alt_installables) > 0:
            return JsonResponse(InstallableSerializer(alt_installables[0]).data)

        type_mapping = {
            'unrestricted': 0,
            'repository_suite_definition': 2,
        }

        installable = Installable(
            name=data['name'],
            synopsis=data['synopsis'],
            description=data['description'],
            remote_repository_url= data['remote_repository_url'],
            repository_type=type_mapping.get(data['type'], 0),
            owner=user_extension.user
        )
        installable.save()
        for tag in tags:
            installable.tags.add(tag)
        installable.save()
        return JsonResponse(InstallableSerializer(installable).data)
    else:
        data = [
            {
                # TODO?
                # 'deleted': False,
                # 'deprecated': False,
                'homepage_url': repo.homepage_url,
                'id': repo.id,
                'model_class': 'Repository',
                'name': repo.name,
                'owner': repo.owner.username,
                # 'private': False,
                'remote_repository_url': repo.remote_repository_url,
                # 'times_downloaded'
                'type': repo.repository_type,
                'user_id': repo.owner.id,
                'category_ids': [x.id for x in repo.tags.all()],
            }
            for repo in Installable.objects.all()
        ]
        return JsonResponse(data, json_dumps_params={'indent': 2}, safe=False)

@csrf_exempt
def v1_repo_detail(request, pk=None):
    repo = get_object_or_404(Installable, pk=pk)
    data = {
        'deleted': False,
        'deprecated': False,
        'homepage_url': repo.homepage_url,
        'id': repo.id,
        'model_class': 'Repository',
        'name': repo.name,
        'owner': repo.owner.username,
        'private': False,
        'remote_repository_url': repo.remote_repository_url,
        'times_downloaded': repo.total_downloads,
        'type': repo.repository_type,
        'user_id': repo.owner.id,
        'changesets': [x.id for x in repo.version_set.all()],
        'category_ids': [x.id for x in repo.tags.all()],
    }
    return JsonResponse(data, json_dumps_params={'indent': 2})

@csrf_exempt
def v1_rev_cr(request, pk=None):
    repo = get_object_or_404(Installable, pk=pk)
    user_extension = user_or_none(request)
    if user_extension is None:
        return HttpResponse('Unauthorized', status=401)

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Save file to disk
            temp = tempfile.NamedTemporaryFile(prefix='shed.upload.', delete=False)
            for chunk in request.FILES['file'].chunks():
                temp.write(chunk)
            temp.close()
            commit_message = request.POST.get('commit_message', '')

            try:
                version = process_tarball(
                    user_extension.user,
                    temp.name,
                    repo,
                    commit_message,
                    sha=None,
                    sig=None
                )
                if isinstance(version, Version):
                    return JsonResponse(VersionSerializer(version).data)
                elif isinstance(version, SuiteVersion):
                    return JsonResponse(SuiteVersionSerializer(version).data)
                else:
                    return JsonResponse({'error': 'unknown model'}, status=400)
            except AssertionError, ae:
                import traceback
                print traceback.format_exc()
                return JsonResponse({'error': 'malformed query', 'message': str(ae)}, status=400)
            except Exception, e:
                import traceback
                print traceback.format_exc()
                return JsonResponse({'error': 'malformed query', 'message': str(e)}, status=400)
            finally:
                if os.path.exists(temp.name):
                    os.unlink(temp.name)

        return JsonResponse({'error': 'malformed query'}, status=400)
    else:
        return JsonResponse({'error': 'unexpected method'}, status=400)

@csrf_exempt
def v1_rev_detail(request, pk=None, pk2=None):
    repo = get_object_or_404(Installable, pk=pk)
    rev = repo.version_set.get(pk=pk2)
    data = {
        'installable_id': rev.installable.id,
    }

    for prop in ('tar_gz_sha256', 'tar_gz_sig_available', 'downloads',
                 'version', 'commit_message', 'uploaded'):
        data[prop] = getattr(rev, prop, None)

    return JsonResponse(data, json_dumps_params={'indent': 2})

def v1_user_list(request):
    data = [
        {
            'username': user.display_name,
            'model_class': 'User',
            'url': reverse('api-planemo-user-detail', kwargs={'pk': user.user.id}),
            'id': user.user.id,
        }
        for user in UserExtension.objects.all()
    ]
    return JsonResponse(data, json_dumps_params={'indent': 2}, safe=False)
    pass

def v1_user_detail(request, pk=None):
    user = get_object_or_404(UserExtension, pk=pk)
    data = {
        'username': user.display_name,
        'model_class': 'User',
        'url': reverse('api-planemo-user-detail', kwargs={'pk': user.user.id}),
        'id': user.user.id,
    }
    return JsonResponse(data, json_dumps_params={'indent': 2})

def v1_cat_list(request):
    data = [
        {
            'description': 'tag.description',
            'deleted': False,
            'url': reverse('api-planemo-cat-detail', kwargs={'pk': tag.id}),
            'model_class': 'Category',
            'id': tag.id,
            'name': tag.display_name,
        }
        for tag in Tag.objects.all()
    ]
    return JsonResponse(data, json_dumps_params={'indent': 2}, safe=False)

@csrf_exempt
def v1_cat_detail(request, pk=None):
    tag = get_object_or_404(Tag, pk=pk)
    data = {
        'description': 'tag.description',
        'deleted': False,
        'url': reverse('api-planemo-cat-detail', kwargs={'pk': tag.id}),
        'model_class': 'Category',
        'id': tag.id,
        'name': tag.display_name,
    }
    return JsonResponse(data, json_dumps_params={'indent': 2})

def v1_download(request):
    pass

@csrf_exempt
def v1_search(request):
    query = request.GET.get('q', '')
    page_size = int(request.GET.get('page_size', '10'))
    page = int(request.GET.get('page', '1'))

    results = []

    data = {
        'total_results': len(results),
        'hostname': 'why-is-this-needed???',
        'page_size': page_size,
        'page': page,
        'hits': results
    }
    return JsonResponse(data, json_dumps_params={'indent': 2})

# TODO:
# var sharable_url = this.options.shed.url + '/view/' + repository.repo_owner_username + '/' + repository.name;

def v1_baseauth(request):
    username, password = base64.b64decode(request.META['HTTP_AUTHORIZATION']).split(':', 1)
    # TODO: Support auth by email, rather than requiring username
    user = authenticate(username=username, password=password)
    if user is not None:
        return JsonResponse({'api_key': user.userextension.api_key})
    return JsonResponse({"error": "Incorrect authentication details"})
