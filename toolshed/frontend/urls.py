"""urlconf for the frontend application"""
from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = patterns(
    'frontend.views',
)


if settings.DEBUG:
    for directory in ('css', 'js', 'bower_components', 'partials'):
        dp = '/%s/' % directory
        urlpatterns += static(dp, document_root=settings.STATICFILES_DIRS[0] + dp)

    urlpatterns += url(r'^$', 'django.contrib.staticfiles.views.serve',
                       kwargs={'path': 'index.html'}),
