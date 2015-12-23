from django.conf.urls import url, patterns, include
from .viewsets import \
    TagListViewSet, \
    TagDetailViewSet, \
    RevisionViewSet, \
    InstallableList, \
    InstallableDetail, \
    SuiteRevisionViewSet, \
    UserViewSet, \
    GroupViewSet


urlpatterns = patterns(
    'api.views',
    # Custom route for handling uploads, registered BEFORE other API routes
    # url(r'^create_revision$', 'register'),
    # Automatic API routes
    # Manual API routes when LIST/DETAIL views use different serializers
    # url(r'^installables/(?P<pk>[0-9]+)(.*)$', InstallableDetail.as_view()),
    # url(r'^installables(.*)$', InstallableList.as_view()),

    # url(r'^tags/(?P<pk>[0-9]+)(.*)$', TagDetailViewSet.as_view()),
    # url(r'^tags(.*)$', TagListViewSet.as_view()),

    # url(r'^uploads$', 'list_uploads'),
    # url(r'^uploads/(?P<name>[0-9]+)$', 'list_upload_folder'),
    # url(r'^uploads/(?P<name>[0-9]+)/(?P<path>.*)$', 'download_file'),
)
