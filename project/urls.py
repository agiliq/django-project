from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

from rss import *

urlpatterns = patterns('project.foo',
    (r'^foo/$', direct_to_template, {'template':'project/dummy.html'}),
    (r'^projson/(?P<project_name>\w+)/$', 'proj_json')
    )

urlpatterns += patterns('project.main',
    # Example:
    (r'^$', 'index'),
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^dashboard/$', 'dashboard'),
    (r'^(?P<project_name>\w+)/$', 'project_details'),
    (r'^(?P<project_name>\w+)/logs/$', 'full_logs'),
    (r'^(?P<project_name>\w+)/noticeboard/$', 'noticeboard'),    
    (r'^(?P<project_name>\w+)/todo/$', 'todo'),
)

urlpatterns += patterns('project.tasks',
    (r'^(?P<project_name>\w+)/tasks/$', 'project_tasks'),                        
    (r'^(?P<project_name>\w+)/taskdetails/(?P<task_num>\d+)/$', 'task_details'),
    (r'^(?P<project_name>\w+)/taskdetails/(?P<task_num>\d+)/addnote/$', 'add_task_note'),
    (r'^(?P<project_name>\w+)/edittask/(?P<task_num>\d+)/$', 'edit_task'),
    (r'^(?P<project_name>\w+)/taskrevision/(?P<task_id>\d+)/$', 'task_revision'),
    (r'^(?P<project_name>\w+)/edititem/(?P<taskitem_num>\d+)/$', 'edit_task_item'),
    (r'^(?P<project_name>\w+)/itemrevision/(?P<taskitem_id>\d+)/$', 'taskitem_revision'),
    (r'^(?P<project_name>\w+)/taskitemhist/(?P<taskitem_num>\d+)/$', 'taskitem_history'),
    )

urlpatterns += patterns('project.wiki',
    (r'^(?P<project_name>\w+)/wiki/$', 'wiki'),
    (r'^(?P<project_name>\w+)/wiki/new/$', 'create_wikipage'),
    (r'^(?P<project_name>\w+)/wiki/(?P<page_name>\w+)/$', 'wikipage'),
    (r'^(?P<project_name>\w+)/wiki/(?P<page_name>\w+)/edit/$', 'edit_wikipage'),
    (r'^(?P<project_name>\w+)/wiki/(?P<page_name>\w+)/revisions/(?P<revision_id>\d+)/$', 'wiki_revision'),
    )

urlpatterns += patterns('project.metrics',
    (r'^(?P<project_name>\w+)/health/$', 'project_health'),
    (r'^(?P<project_name>\w+)/userstats/$', 'user_stats'),
    )                       

urlpatterns += patterns('project.files',
    (r'^(?P<project_name>\w+)/files/$', 'files'),
    )


urlpatterns += patterns('project.users',
    (r'^accounts/login/$', 'login'),
    (r'^accounts/logout/$', 'logout'),
    (r'^accounts/profile/$', 'profile'),
    (r'^accounts/register/$', 'register'),
    (r'^(?P<project_name>\w+)/user/(?P<username>\w+)/$', 'user_details'),
    )

urlpatterns += patterns('project.json.task',
    (r'json/(?P<project_name>\w+)/task/show/(?P<task_id>\d+)/$', 'show_task'),                        
    )

feeds = {
    'project': ProjectRss,
}
urlpatterns += patterns('',
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    )

urlpatterns += patterns('',
        (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'G:/prajact/project/templates/site_media'}),
    )




