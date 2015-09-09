"""urlconf for the base application"""

from django.conf.urls import url, patterns
from django.views.generic import TemplateView
# from .views import GalaxyInstanceView
# from .views import GalaxyInstanceListView

urlpatterns = patterns('base.views',
    # url(r'^$', TemplateView.as_view(template_name='base/home.html'), name='home'),
)

