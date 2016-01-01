from django.conf.urls import url
from .views import v1_index, \
    v1_repo_list, v1_repo_detail, v1_rev_detail, \
    v1_cat_list, v1_cat_detail, \
    v1_user_list, v1_user_detail, \
    v1_download, v1_baseauth

PK = '(?P<pk>[0-9]+)'
PK2 = '(?P<pk2>[0-9]+)'

urlpatterns = [
    url(r'v1/$', v1_index),

    url(r'v1/api/authenticate/baseauth$', v1_baseauth),

    url(r'v1/api/users/$', v1_user_list, name='api-planemo-user-list'),
    url(r'v1/api/users/' + PK, v1_user_detail, name='api-planemo-user-detail'),

    url(r'v1/api/categories/$', v1_cat_list, name='api-planemo-cat-list'),
    url(r'v1/api/categories/' + PK + '/$', v1_cat_detail, name='api-planemo-cat-detail'),
    url(r'v1/api/repository/download/', v1_download),

    url(r'v1/api/repositories/$', v1_repo_list, name='api-planemo-repo-list'),
    url(r'v1/api/repositories/' + PK + '/$', v1_repo_detail),
    url(r'v1/api/repositories/' + PK + '/changeset_revision/' + PK2, v1_rev_detail),
]
