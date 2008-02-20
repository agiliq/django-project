from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms
from defaults import *

def project_tasks(request, project_name):
    """Displays all the top tasks and task items for a specific project.
    shows top tasks
    shows sub tasks name for top tasks
    shows task items for the top tasks
    shows add a top task form
    """
    project = get_project(request, project_name)
    if request.GET.get('includecomplete', 0):
        query_set = project.task_set.filter(parent_task_num__isnull = True)
    else:
        query_set = project.task_set.filter(parent_task_num__isnull = True, is_complete = False)
    tasks, page_data = get_paged_objects(query_set, request, tasks_on_tasks_page)
    
    if request.method == 'POST':
        if request.POST.has_key('addtask'):
            taskform = bforms.CreateTaskForm(project, request.POST)
            if taskform.is_valid():
                taskform.save()
                return HttpResponseRedirect('.')
        elif request.POST.has_key('markdone') or request.POST.has_key('markundone'):
            return handle_task_status(request)
        elif request.has_key('deletetask'):
            return delete_task(request)
    if request.method == 'GET':
        taskform = bforms.CreateTaskForm(project)
        
    payload = {'project':project, 'tasks':tasks, 'taskform':taskform, 'page_data':page_data}    
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
    task = Task.objects.get(project = project, number = task_num)
    
    addsubtaskform = bforms.CreateSubTaskForm(project, task)
    additemform = bforms.CreateTaskItemForm(project, task)
    
    if request.method == 'POST':
        if request.POST.has_key('addsubtask'):
            addsubtaskform = bforms.CreateSubTaskForm(project, task, request.POST)
            if addsubtaskform.is_valid():
                addsubtaskform.save()
                return HttpResponseRedirect('.')
        elif request.POST.has_key('additem'):
            additemform = bforms.CreateTaskItemForm(project, task, request.POST)
            if additemform.is_valid():
                additemform.save()
                return HttpResponseRedirect('.')
        elif request.POST.has_key('addnote'):
            noteform = bforms.AddTaskNoteForm(task, request.user, request.POST)
            if noteform.is_valid():
                noteform.save()
                return HttpResponseRedirect('.')
        elif request.POST.has_key('markdone') or request.POST.has_key('markundone'):
            return handle_task_status(request)
        elif request.POST.has_key('itemmarkdone') or request.POST.has_key('itemmarkundone'):
            return handle_taskitem_status(request)
    if request.method == 'GET':
        addsubtaskform = bforms.CreateSubTaskForm(project, task)
        additemform = bforms.CreateTaskItemForm(project, task)
        noteform = bforms.AddTaskNoteForm(task, request.user)
    payload = {'project':project, 'task':task, 'addsubtaskform':addsubtaskform, 'additemform':additemform, 'noteform':noteform}
    return render(request, 'project/taskdetails.html', payload)

def edit_task(request, project_name, task_num):
    """
    Edit a given task
    """
    project = get_project(request, project_name)
    task = Task.objects.get(project = project, number = task_num)
    if request.method == 'POST':
        editform = bforms.EditTaskForm(data = request.POST, task = task, project = project)
        if editform.is_valid():
            task = editform.save()
            return HttpResponseRedirect(task.get_absolute_url())
    if request.method == 'GET':        
        editform = bforms.EditTaskForm(project = project, task = task)
        
    payload = {'project':project, 'task':task, 'editform':editform}
    return render(request, 'project/edittask.html', payload)
    
    

def task_revision(request, project_name, task_id):
    """
    Shows a specific revision of the code.
    """
    project = get_project(request, project_name)
    task = Task.all_objects.get(project = project, id = task_id)
    if request.method == 'POST':
        print request.POST
        prevlatest = Task.objects.get(project = project, number = task.number)
        task.save()
        prevlatest.is_current = False
        prevlatest.save_without_versioning()
    payload = {'project':project, 'task':task,}
    return render(request, 'project/taskrevision.html', payload)

def add_task_note(request, project_name, task_num):
    """
    Add notes to a task.
    """
    project = get_project(request, project_name)
    task = Task.objects.get(project = project, number = task_num)
    if request.method == 'POST':
        noteform = bforms.AddTaskNoteForm(task, request.user, request.POST)
        if noteform.is_valid():
            noteform.save()
            return HttpResponseRedirect(task.get_absolute_url())
    if request.method == 'GET':
        noteform = bforms.AddTaskNoteForm(task, request.user)
    payload = {'project':project, 'task':task, 'noteform':noteform}
    return render(request, 'project/addtasknote.html', payload)

def edit_task_item(request, project_name, taskitem_num):
    """Edit a task item."""
    project = get_project(request, project_name)
    taskitem = TaskItem.objects.get(project = project, number = taskitem_num)
    if request.method == 'POST':
        itemform = bforms.EditTaskItemForm(request.POST, instance = taskitem)
        if itemform.is_valid():
            item = itemform.save()
            return HttpResponseRedirect(item.task.get_absolute_url())
    elif request.method == 'GET':
        itemform = bforms.EditTaskItemForm(instance = taskitem)
    payload = {'project':project, 'taskitem':taskitem, 'itemform':itemform}
    return render(request, 'project/edititem.html', payload)
    

def taskitem_revision(request, project_name, taskitem_id):
    """Shows taskitem history for a given item.
    Allows to rollback to a specific version."""
    project = get_project(request, project_name)
    taskitem = TaskItem.all_objects.get(project = project, id = taskitem_id)
    if request.method == 'POST':
        prevlatest = TaskItem.objects.get(project = taskitem.project, number = taskitem.number)
        newtaskitem.save()
        prevlatest.is_current = False
        prevlatest.save_without_versioning()
        return HttpResponseRedirect(taskitem.task.get_absolute_url())
    payload = {'project':project, 'taskitem':taskitem,}
    return render(request, 'project/taskitemrev.html', payload)
    

def taskitem_history(request, project_name, taskitem_num):
    """Shows taskitem history for a given item.
    Allows to rollback to a specific version."""
    pass
