from django.conf.urls.defaults import *

urlpatterns = patterns('project.main',
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
    (r'^(?P<project_name>\w+)/taskdetails/(?P<task_num>)/$', 'task_details'),
    (r'^(?P<project_name>\w+)/taskhistory/(?P<task_num>)/$', 'task_history'),
    (r'^(?P<project_name>\w+)/taskitemhist/(?P<taskitem_num>)/$', 'taskitem_history'),
    )

urlpatterns += patterns('project.wiki',
    (r'^(?P<project_name>\w+)/wiki/$', 'wiki'),
    (r'^(?P<project_name>\w+)/wiki/new/$', 'create_wikipage'),
    (r'^(?P<project_name>\w+)/wiki/(?P<page_name>)/$', 'wikipage'),
    (r'^(?P<project_name>\w+)/wiki/(?P<page_name>)/edit/$', 'edit_wikipage'),
    #(r'^(?P<project_name>\w+)/wiki/(?P<page_name>)/revisions/$', 'wiki_revisions'),
    (r'^(?P<project_name>\w+)/wiki/(?P<page_name>)/revisions/(?P<revision_id>)/$', 'wiki_revision'),
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
    (r'^profile/$', 'profile'),
    (r'^register/$', 'register'),
    )


