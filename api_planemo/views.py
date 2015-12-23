from django.http import JsonResponse
from base.models import Installable, UserExtension, Tag
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse


# Create your views here.
def v1_index(request):
    return JsonResponse({'hi': 'hi'})


def v1_repo_list(request):
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
        'changesets': [x.id for x in repo.revision_set.all()],
        'category_ids': [x.id for x in repo.tags.all()],
    }
    return JsonResponse(data, json_dumps_params={'indent': 2})

def v1_rev_detail(request, pk=None, pk2=None):
    repo = get_object_or_404(Installable, pk=pk)
    rev = repo.revision_set.get(pk=pk2)
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
