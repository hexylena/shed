"""urlconf for the base application"""

from django.conf.urls import url, patterns, include
# from django.views.generic import TemplateView
# from .views import GalaxyInstanceView
# from .views import GalaxyInstanceListView
from rest_framework import routers
from .viewsets import TagViewSet, RevisionViewSet, InstallableViewSet, SuiteRevisionViewSet


router = routers.DefaultRouter()
router.register(r'tags', TagViewSet)
router.register(r'suiterevisions', SuiteRevisionViewSet)
router.register(r'revisions', RevisionViewSet)
router.register(r'installables', InstallableViewSet)

urlpatterns = patterns(
    'base.views',
    url(r'^', include(router.urls)),
    # url(r'^$', TemplateView.as_view(template_name='base/home.html'), name='home'),
)
