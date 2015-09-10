"""urlconf for the frontend application"""
from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = patterns(
    'frontend.views',
)


# Serve everything out of settings.STATICFILES_DIRS
# This isn't the cleanest or most beautiful thing in the world, but it works,
# and that's what matters.
#
# In a real deployment scenario, django will use X-SENDFILE to provide access
# to actual archives/static resources.
if settings.DEBUG:
    for directory in ('css', 'js', 'bower_components', 'partials'):
        dp = '/%s/' % directory
        urlpatterns += static(dp, document_root=settings.STATICFILES_DIRS[0] + dp)

    urlpatterns += url(r'^$', 'django.contrib.staticfiles.views.serve',
                       kwargs={'path': 'index.html'}),
