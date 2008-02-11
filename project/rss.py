from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms

from django.contrib.syndication.feeds import FeedDoesNotExist, Feed

class ProjectRss(Feed):
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
        
        
"""class BeatFeed(Feed):
    def get_object(self, bits):
        # In case of "/rss/beats/0613/foo/bar/baz/", or other such clutter,
        # check that bits has only one member.
        if len(bits) != 1:
            raise ObjectDoesNotExist
        return Beat.objects.get(beat__exact=bits[0])

    def title(self, obj):
        return "Chicagocrime.org: Crimes for beat %s" % obj.beat

    def link(self, obj):
        if not obj:
            raise FeedDoesNotExist
        return obj.get_absolute_url()

    def description(self, obj):
        return "Crimes recently reported in police beat %s" % obj.beat

    def items(self, obj):
        return Crime.objects.filter(beat__id__exact=obj.id).order_by('-crime_date')[:30]        
"""    
    
