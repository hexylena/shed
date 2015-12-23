from django.conf.urls import url, include
from rest_framework import routers
from .viewsets import \
    TagListViewSet, \
    TagDetailViewSet, \
    VersionViewSet, \
    InstallableList, \
    InstallableDetail, \
    SuiteVersionViewSet, \
    UserViewSet, \
    GroupViewSet
from .views import register


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
# router.register(r'tags', TagViewSet)
router.register(r'suiteversions', SuiteVersionViewSet)
router.register(r'versions', VersionViewSet)


urlpatterns = [
    # Custom route for handling uploads, registered BEFORE other API routes
    url(r'create_version$', register),
    # Manual API routes when LIST/DETAIL views use different serializers
    # These are not listed in the API index unfortunately. TODO! http://www.django-rest-framework.org/api-guide/routers/
    url(r'installables/(?P<pk>[0-9]+)(.*)$', InstallableDetail.as_view()),
    url(r'installables(.*)$', InstallableList.as_view()),

    url(r'tags/(?P<pk>[0-9]+)(.*)$', TagDetailViewSet.as_view()),
    url(r'tags(.*)$', TagListViewSet.as_view()),
    # Automatic API routes
    url(r'', include(router.urls)),
]
