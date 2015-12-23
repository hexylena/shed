from django.conf.urls import url, patterns, include
# from shed.api_planemo import urls as planemo_api
from .views import v1

urlpatterns = [
    url(r'v1', v1),
]
