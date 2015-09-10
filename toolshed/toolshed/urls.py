from django.conf.urls import include, url
from django.contrib import admin
from .views import github


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-token-auth/', 'rest_framework_jwt.views.obtain_jwt_token'),
    url(r'^api-token-refresh/', 'rest_framework_jwt.views.refresh_jwt_token'),
    url(r'^api-token-verify/', 'rest_framework_jwt.views.verify_jwt_token'),

    url('', include('frontend.urls')),
    url('^api/', include('api.urls')),

    url(r'^auth/github$', github),
]
