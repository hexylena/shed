from django.conf.urls import url, patterns, include
from rest_framework import routers
from .viewsets import \
    TagListViewSet, \
    TagDetailViewSet, \
    RevisionViewSet, \
    InstallableList, \
    InstallableDetail, \
    SuiteRevisionViewSet, \
    UserViewSet, \
    GroupViewSet


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
# router.register(r'tags', TagViewSet)
router.register(r'suiterevisions', SuiteRevisionViewSet)
router.register(r'revisions', RevisionViewSet)


urlpatterns = patterns(
    # Custom route for handling uploads, registered BEFORE other API routes
    url(r'create_revision$', 'register'),
    # Automatic API routes
    url(r'', include(router.urls)),
    # Manual API routes when LIST/DETAIL views use different serializers
    url(r'installables/(?P<pk>[0-9]+)(.*)$', InstallableDetail.as_view()),
    url(r'installables(.*)$', InstallableList.as_view()),

    url(r'tags/(?P<pk>[0-9]+)(.*)$', TagDetailViewSet.as_view()),
    url(r'tags(.*)$', TagListViewSet.as_view()),
)
