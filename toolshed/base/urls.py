"""urlconf for the base application"""

from django.conf.urls import url, patterns, include
# from django.views.generic import TemplateView
# from .views import GalaxyInstanceView
# from .views import GalaxyInstanceListView
from rest_framework import routers
from .viewsets import TagViewSet, RevisionViewSet, InstallableList, InstallableDetail, SuiteRevisionViewSet, UserViewSet, GroupViewSet


router = routers.DefaultRouter(trailing_slash=False)
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'tags', TagViewSet)
router.register(r'suiterevisions', SuiteRevisionViewSet)
router.register(r'revisions', RevisionViewSet)
# router.register(r'installables', InstallableViewSet)

# ^ ^suiterevisions$ [name='suiterevision-list']
# ^ ^suiterevisions\.(?P<format>[a-z0-9]+)/?$ [name='suiterevision-list']
# ^ ^suiterevisions/(?P<pk>[^/.]+)$ [name='suiterevision-detail']
# ^ ^suiterevisions/(?P<pk>[^/.]+)\.(?P<format>[a-z0-9]+)/?$ [name='suiterevision-detail']


urlpatterns = patterns(
    'base.views',
    url(r'^', include(router.urls)),

    url(r'^installables/(?P<pk>[0-9]+)(.*)$', InstallableDetail.as_view()),
    url(r'^installables(.*)$', InstallableList.as_view()),

    # url(r'^$', TemplateView.as_view(template_name='base/home.html'), name='home'),
)
