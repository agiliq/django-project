from django.utils import simplejson
from django.http import HttpResponse
from helpers import *

def proj_json(request, project_name):
    project = get_project(request, project_name)
    tasks = project.task_set.filter()
    items = []
    for task in tasks:
        print 'foo', task
        children = [
          { 'name':'Cinammon Roll', 'type':'poptart' },
          { 'name':'Brown Sugar Cinnamon', 'type':'poptart' },
          { 'name':'French Toast', 'type':'poptart' }
       ]
        children = []
        for subtask in task.task_set.all():
            children.append({'_reference':subtask.name})
        task = {'name':task.name, 'type':'task', 'children':children}
        items.append(task)
            
        print items
    payload = { 'label': 'name',
    'identifier': 'name',
    'items': 
    items
    }   
    return HttpResponse(simplejson.dumps(payload), mimetype="application/javascript") 
    