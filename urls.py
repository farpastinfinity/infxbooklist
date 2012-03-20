from django.conf.urls.defaults import *
import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/', include(admin.site.urls)),
    (r'^admin/booklistapp', include(admin.site.urls)),
    (r'^feedback/$', 'infxbooklist.booklistapp.views.feedback'),
    (r'^edit/$', 'infxbooklist.booklistapp.views.edit'),
    (r'^add/$', 'infxbooklist.booklistapp.views.add'),
    (r'^delete/$', 'infxbooklist.booklistapp.views.delete'),
    (r'^update/$', 'infxbooklist.booklistapp.views.update'),
    (r'^updateprofile/$', 'infxbooklist.booklistapp.views.updateprofile'),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout'),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    (r'^adminmedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.ADMIN_MEDIA_ROOT }),
    (r'^profile/$', 'infxbooklist.booklistapp.views.profile'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^(?P<path>favicon\.ico)$', 'django.views.static.serve',
            {'document_root': 'static'}),
        (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': 'static'}),
        (r'^bookcovers/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': 'bookcovers'}),
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,}),
    )
    
urlpatterns += patterns('',
    (r'^((?P<category>.*)/$|$)', 'infxbooklist.booklistapp.views.index'),
)
