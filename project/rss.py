from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms

import basicauth
from django.contrib.syndication.views import Feed as feed_view


class ProjectRss(feed_view):
    """Returns the feed for a project."""
    def get_object(self, bits):
        if not len(bits) == 1:
            raise ObjectDoesNotExist('No such feed.')
        else:
            project = Project.objects.get(shortname = bits[0])
            return project
        
    def title(self, obj):
        return 'Feed for project %s' % obj.name
    
    def link(self, obj):
        return obj.get_absolute_url()
    
    def description(self, obj):
        return 'Feed for project %s' % obj.name
    
    
    def items(self, obj):
        return obj.log_set.all()[:30]
   
@basicauth.logged_in_or_basicauth()    
def proj_feed(request, url, feed_dict=None):
    slug, param = url.split('/', 1)
    project_name = param
    project = get_project(request, project_name)
    return feed_view(request, url, feed_dict)

