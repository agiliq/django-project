from django.utils import simplejson
from django.http import HttpResponse
from project.helpers import *
from project.models import *

def show_task(request, project_name, task_id):
    project = get_project(request, project_name)
    task = Task.objects.get(project = project, id = task_id)
    print task
    return HttpResponse(simplejson.dumps(task.name))