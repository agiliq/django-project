from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms
from defaults import *
import diff_match_patch
import defaults

def project_tasks(request, project_name):
    """Displays all the top tasks and task items for a specific project.
    shows top tasks
    shows sub tasks name for top tasks
    shows task items for the top tasks
    shows add a top task form
    Actions available here:
    Create a new task: Owner Participant
    Mark task as done: Owner Participant
    Delete Task: Owner Participant
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    if request.GET.get('includecomplete', 0):
        query_set = project.task_set.filter(parent_task_num__isnull = True)
    else:
        query_set = project.task_set.filter(parent_task_num__isnull = True, is_complete = False)
    tasks, page_data = get_paged_objects(query_set, request, tasks_on_tasks_page)
    
    if request.method == 'POST':
        if request.POST.has_key('addtask'):
            taskform = bforms.CreateTaskForm(project, request.user, request.POST)
            if taskform.is_valid():
                taskform.save()
                return HttpResponseRedirect('.')
        elif request.POST.has_key('markdone') or request.POST.has_key('markundone'):
            return handle_task_status(request)
        elif request.has_key('deletetask'):
            return delete_task(request)
    if request.method == 'GET':
        taskform = bforms.CreateTaskForm(project, request.user)
    
    if request.GET.get('csv', ''):
        response, writer = reponse_for_cvs(project=project)
        writer.writerow(Task.as_csv_header())
        for task in tasks:
            writer.writerow(task.as_csv())
        return response
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
    Actions available here:
    Create a new subtask task: Owner Participant
    Create a new taskitem: Owner Participant
    Add note to task: Owner Participant
    Mark item done: Owner Participant
    Mar item undone: Owner Participant 
    """
    
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    task = Task.objects.get(project = project, number = task_num)
    
    addsubtaskform = bforms.CreateSubTaskForm(project, task)
    additemform = bforms.CreateTaskItemForm(project, request.user, task)
    
    if request.method == 'POST':
        if request.POST.has_key('addsubtask'):
            
            addsubtaskform = bforms.CreateSubTaskForm(project, request.user, task, request.POST)
            if addsubtaskform.is_valid():
                addsubtaskform.save()
                return HttpResponseRedirect('.')
        elif request.POST.has_key('additem'):
            additemform = bforms.CreateTaskItemForm(project, request.user, task, request.POST)
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
        addsubtaskform = bforms.CreateSubTaskForm(project, request.user, task)
        additemform = bforms.CreateTaskItemForm(project, request.user, task)
        noteform = bforms.AddTaskNoteForm(task, request.user)
    if request.GET.get('csv', ''):
        response, writer = reponse_for_cvs(project=project)
        writer.writerow(Task.as_csv_header())
        writer.writerow(task.as_csv())
        return response
    payload = {'project':project, 'task':task, 'addsubtaskform':addsubtaskform, 'additemform':additemform, 'noteform':noteform}
    return render(request, 'project/taskdetails.html', payload)

def edit_task(request, project_name, task_num):
    """
    Edit a given task.
    Actions avialble here:
    Edit Task: Owner Participant
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    task = Task.objects.get(project = project, number = task_num)
    if request.method == 'POST':
        editform = bforms.EditTaskForm(data = request.POST, user = request.user, task = task, project = project)
        if editform.is_valid():
            task = editform.save()
            return HttpResponseRedirect(task.get_absolute_url())
    if request.method == 'GET':        
        editform = bforms.EditTaskForm(project, request.user, task)
    if request.GET.get('csv', ''):
        response, writer = reponse_for_cvs(project=project)
        writer.writerow(Task.as_csv_header())
        writer.writerow(task.as_csv())        
        return response          
    payload = {'project':project, 'task':task, 'editform':editform}
    return render(request, 'project/edittask.html', payload)
    
    

def task_revision(request, project_name, task_id):
    """
    Shows a specific revision of the code.
    Actions available here.
    Rollback task to a revision.  Owner Participant
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    task = Task.all_objects.get(project = project, id = task_id)
    if request.method == 'POST':
        print request.POST
        prevlatest = Task.objects.get(project = project, number = task.number)
        task.save()
        prevlatest.is_current = False
        prevlatest.save_without_versioning()
    if request.GET.get('csv', ''):
        response, writer = reponse_for_cvs(project=project)
        writer.writerow(Task.as_csv_header())
        writer.writerow(task.as_csv())        
        return response        
    payload = {'project':project, 'task':task,}
    return render(request, 'project/taskrevision.html', payload)

def add_task_note(request, project_name, task_num):
    """
    Add notes to a task.
    Actions available here:
    Add a note:  Owner Participant
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
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
    """Edit a task item.
    Action available here:
    Edit a task item:  Owner Participant
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    taskitem = TaskItem.objects.get(project = project, number = taskitem_num)
    if request.method == 'POST':
        itemform = bforms.EditTaskItemForm(project, request.user, taskitem, request.POST)
        if itemform.is_valid():
            item = itemform.save()
            return HttpResponseRedirect(item.task.get_absolute_url())
    elif request.method == 'GET':
        itemform = bforms.EditTaskItemForm(project, request.user, taskitem)
        
    if request.GET.get('csv', ''):
        response, writer = reponse_for_cvs(project=project)
        writer.writerow(TaskItem.as_csv_header())
        writer.writerow(taskitem.as_csv())
        return response
    payload = {'project':project, 'taskitem':taskitem, 'itemform':itemform}
    return render(request, 'project/edititem.html', payload)
    

def taskitem_revision(request, project_name, taskitem_id):
    """Shows taskitem history for a given item.
    Actions available here:
    Rollback taskitem to a specific version:  Owner Participant
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    taskitem = TaskItem.all_objects.get(project = project, id = taskitem_id)
    if request.method == 'POST':
        prevlatest = TaskItem.objects.get(project = taskitem.project, number = taskitem.number)
        newtaskitem.save()
        prevlatest.is_current = False
        prevlatest.save_without_versioning()
        return HttpResponseRedirect(taskitem.task.get_absolute_url())
    if request.GET.get('csv', ''):
        response, writer = reponse_for_cvs(project=project)
        writer.writerow(TaskItem.as_csv_header())
        writer.writerow(taskitem.as_csv())
        return response
    payload = {'project':project, 'taskitem':taskitem,}
    return render(request, 'project/taskitemrev.html', payload)

def task_history(request, project_name, task_num):
    """Shows taskitem history for a given item.
    Shows summary of each revision.
    Actions available here:
    Diffing between versions:  Owner Participant Viewer
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    task = Task.objects.get(project = project, number = task_num)
    version1 = int(request.GET.get('version1', 0))
    version2 = int(request.GET.get('version2', 0))
    if version1 and version2:
        taskver1 = Task.all_objects.get(project = project, id = version1)
        taskver2 = Task.all_objects.get(project = project, id = version2)
        app = diff_match_patch.diff_match_patch()
        diff = app.diff_main(taskver1.as_text(), taskver2.as_text())
        app.diff_cleanupSemantic(diff)
        htmldiff = app.diff_prettyHtml(diff)
        payload = {'project':project, 'task':task,'ver1':taskver1, 'ver2':taskver2, 'diff':htmldiff}
        return render(request, 'project/taskdiffresults.html', payload)
    else:
        payload = {'project':project, 'task':task}
        return render(request, 'project/taskhistory.html', payload)
    
def taskitem_history(request, project_name, taskitem_num):
    """Shows taskitem history for a given item.
    Actions available here:
    Diffing between versions:  Owner Participant Viewer
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    taskitem = TaskItem.objects.get(project = project, number = taskitem_num)
    version1 = int(request.GET.get('version1', 0))
    version2 = int(request.GET.get('version2', 0))
    if version1 and version2:
        taskitemver1 = TaskItem.all_objects.get(project = project, id = version1)
        taskitemver2 = TaskItem.all_objects.get(project = project, id = version2)
        app = diff_match_patch.diff_match_patch()
        diff = app.diff_main(taskitemver1.as_text(), taskitemver2.as_text())
        app.diff_cleanupSemantic(diff)
        htmldiff = app.diff_prettyHtml(diff)
        payload = {'project':project, 'task':taskitem,'ver1':taskitemver1, 'ver2':taskitemver2, 'diff':htmldiff}
        return render(request, 'project/taskdiffresults.html', payload)
    else:
        payload = {'project':project, 'taskitem':taskitem}
        return render(request, 'project/taskitemhist.html', payload)
    
def tasks_quickentry(request, project_name):
    """Quick entry form for entering tasks.
    Actions available here.
    Create tasks: Owner Participant
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    if request.method == 'POST':
        entry_form = bforms.FormCollection(bforms.AddTaskOrSubTaskForm, {'project':project, 'user':request.user, 'data':request.POST}, defaults.objects_on_quickentry_page)
        if entry_form.is_valid():
            entry_form.save()
            if request.POST.get('AddRedirect'):    
                return HttpResponseRedirect(project.tasks_url())
            else:
                return HttpResponseRedirect('.')
    elif request.method == 'GET':
        entry_form = bforms.FormCollection(bforms.AddTaskOrSubTaskForm, {'project':project, 'user':request.user},  defaults.objects_on_quickentry_page)
    payload = {'project':project, 'entry_form':entry_form}
    return render(request, 'project/tasksquickentry.html', payload)

def taskitems_quickentry(request, project_name):
    """quick entry form for task items.
    Actions available here.
    Create tasksitem: Owner Participant
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    if request.method == 'POST':
        itementry_form = bforms.FormCollection(bforms.TaskItemQuickForm, {'project':project, 'user':request.user, 'data':request.POST},  defaults.objects_on_quickentry_page)
        print itementry_form.is_valid()
        itementry_form.save()
        if request.POST.get('AddRedirect'):    
            return HttpResponseRedirect(project.tasks_url())
        else:
            return HttpResponseRedirect('.')
    elif request.method == 'GET':
        itementry_form = bforms.FormCollection(bforms.TaskItemQuickForm, {'project':project, 'user':request.user},  defaults.objects_on_quickentry_page)
    payload = {'project':project, 'itementry_form':itementry_form}
    return render(request, 'project/taskitemsquickentry.html', payload)

def task_hierachy(request, project_name):
    """SHow the tasks for project as nested list."""
    project = get_project(request, project_name)
    tasks = project.get_task_hierachy()
    tasks = recursive_map(task2task_link, tasks)
    payload = {'project':project, 'tasks':tasks}
    return render(request, 'project/taskhier.html', payload)

def recursive_map(f, l):
    "A helper method to convert nested list."    
    return [isinstance(e, list) and recursive_map(f, e) or f(e) for e in l]

def task2task_link(task):
    from django.utils.safestring import mark_safe
    "contert a task object to a lnk"
    return mark_safe('<a href="%s">%s</a>' % (task.get_absolute_url(), task.name))
    