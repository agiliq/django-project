from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms

def project_tasks(request, project_name):
    """Displays all the top tasks and task items for a specific project.
    shows top tasks
    shows sub tasks name for top tasks
    shows task items for the top tasks
    """
    project = get_project(request, project_name)
    #tasks = project.task_set.filter(parent_task = None)
    tasks = project.task_set.filter(parent_task__isnull = True)
    payload = {'tasks':tasks}
    return render(request, 'project/projecttask.html', payload)

def task_details(request, project_name, task_num):
    """Shows details ofa specific task.
    Shows a specific task.
    Shows its subtasks.
    Shows taskitems.
    Shows notes on the tasks.
    Shows form to add sub task.
    Shows form to add task items.
    Shows notes on taskitems.(?)
    """
    project = get_project(request, project_name)
    task = Task.objects.get(number = task_num)
    if request.method == 'POST':
        addsubtaskform = bforms.CreateSubTaskForm(project, task, request.POST)
        if addsubtaskform.is_valid():
            addsubtaskform.save()
            return HttpResponseRedirect('.')
    if request.method == 'GET':
        addsubtaskform = bforms.CreateSubTaskForm(project, task)
    payload = {'task':task, 'addsubtaskform':addsubtaskform}
    return render(request, 'project/taskdetails.html', payload)

def task_history(request, project_name, task_num):
    """
    Shows tasks history for given task.
    Allows to rol back to a specific revisiosn of the task.
    """
    pass

def taskitem_history(request, project_name, taskitem_num):
    """Shows taskitem history for a given item.
    Allows to rollback to a specific version."""
    pass
