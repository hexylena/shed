from django.conf.urls import url, include

from .views import api_list
from django.contrib import admin
from api_planemo import urls as api_planemo_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'api/planemo', include(api_planemo_urls)),
    url(r'api/', api_list, name='api_list'),
]
