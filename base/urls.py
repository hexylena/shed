from django.conf.urls import url, include

from .views import api_list
from django.contrib import admin
from api_ts_old import urls as api_ts_old_urls
from api_drf import urls as api_drf_urls

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'api/drf/', include(api_drf_urls)),
    url(r'api/toolshed_legacy/', include(api_ts_old_urls)),

    url(r'api/', api_list, name='api_list'),
]
