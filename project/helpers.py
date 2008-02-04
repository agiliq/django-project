from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404

from models import *

def get_project(request, project_name):
    """Returns the project with the given name if the logged in user has access to the project. Raises 404 otherwise."""
    project = Project.objects.get(shortname = project_name)
    try:
        project.subscribeduser_set.get(user = request.user)
    except SubscribedUser.DoesNotExist:
        raise Http404
    return project

def render(request, template, payload):
    """This populates the site wide template context in the payload passed to the template"""
    return render_to_response(template, payload, RequestContext(request))
