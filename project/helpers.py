from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from django.http import HttpResponseRedirect

from django.core.paginator import ObjectPaginator, InvalidPage

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

def get_pagination_data(obj_page, page_num):
    data = {}
    page_num = int(page_num)
    data['has_next_page'] = obj_page.has_next_page(page_num)
    data['next_page'] = page_num + 1
    data['has_prev_page'] = obj_page.has_previous_page(page_num)
    data['prev_page'] = page_num - 1
    data['first_on_page'] = obj_page.first_on_page(page_num)
    data['last_on_page'] = obj_page.last_on_page(page_num)
    data['total'] = obj_page.hits
    return data

def get_paged_objects(query_set, request, obj_per_page):
    try:
        page = request.GET['page']
        page = int(page)
    except KeyError, e:
        page = 0
    object_page = ObjectPaginator(query_set, obj_per_page)
    object = object_page.get_page(page)
    page_data = get_pagination_data(object_page, page)
    return object, page_data

def handle_task_status(request):
    id = request.POST['taskid']
    task = Task.objects.get(id = id)
    if request.POST.has_key('markdone'):
        task.is_complete = True
    else:
        task.is_complete = False
    task.save()
    return HttpResponseRedirect('.')

def handle_taskitem_status(request):
    id = request.POST['taskitemid']
    taskitem = TaskItem.objects.get(id = id)
    if request.POST.has_key('itemmarkdone'):
        taskitem.is_complete = True
    else:
        taskitem.is_complete = False
    taskitem.save()
    return HttpResponseRedirect('.')

def delete_task(request):
    taskid = request.POST['taskid']
    print taskid
    task = Task.objects.get(id = taskid)
    task.delete()
    return HttpResponseRedirect('.')
