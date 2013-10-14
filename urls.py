from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    # Example:
    (r'^', include('project.urls')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
            (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
        )
    
    urlpatterns += patterns('',
            (r'^help/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.HELP_ROOT}),
        )
