from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms

def index(request):
    """If the user is not logged in, show him the login/register forms, with some blurb about the services. Else redirect to /dashboard/"""
    if request.user.is_authenticated():
        return HttpResponseRedirect('/dashboard/')
    payload = {}
    return render(request, 'project/index.html', payload)

@login_required
def dashboard(request):
    """The point of entry for a logged in user.
    Shows the available active projects for the user, and allows him to create one.
    Shows the pending invites to other projects.
    Shows very critical information about available projects.
    """
    user = request.user
    subs = user.subscribeduser_set.all()
    if request.method == 'POST':
        createform = bforms.CreateProjectForm(user, request.POST)
        if createform.is_valid():
            createform.save()
            return HttpResponseRedirect('.')
    elif request.method == 'GET':
        createform = bforms.CreateProjectForm()
    
    payload = {'subs': subs, 'createform':createform}
    return render(request, 'project/dashboard.html', payload)

@login_required
def project_details(request, project_name):
    """
    Point of entry for a specific project.
    Shows the important information for a project.
    Shows form to invite an user.
    Form to create a new top task.
    """
    user = request.user
    project = get_project(request, project_name)
    inviteform = bforms.InviteUserForm()
    taskform = bforms.CreateTaskForm(project)    
    if request.method == 'POST':
        if request.POST.has_key('invite'):
            inviteform = bforms.InviteUserForm(project, request.POST)
            if inviteform.is_valid():
                inviteform.save()
                return HttpResponseRedirect('.')
        elif request.POST.has_key('task'):
            taskform = bforms.CreateTaskForm(project, request.POST)
            if taskform.is_valid():
                taskform.save()
                return HttpResponseRedirect('.')
    if request.method == 'GET':
        inviteform = bforms.InviteUserForm()
        taskform = bforms.CreateTaskForm(project)
    payload = {'project':project, 'inviteform':inviteform, 'taskform':taskform}
    return render(request, 'project/projdetails.html', payload)


@login_required
def full_logs(request, project_name):
    logs = Log.objects.all()
    payload = {'project':project, 'logs':logs}
    return render(request, 'project/fulllogs.html', payload)

@login_required
def noticeboard(request, project_name):
    """A noticeboard for the project.
    Shows the notices posted by the users.
    Shows the add notice form.
    """
    project = get_project(request, project_name)
    notices = Notice.objects.filter(project = project)
    if request.method == 'POST':
        addnoticeform = bforms.AddNoticeForm(project, request.user, request.POST)
        if addnoticeform.is_valid():
            addnoticeform.save()
            return HttpResponseRedirect('.')
    if request.method == 'GET':        
        addnoticeform = bforms.AddNoticeForm()
    payload = {'project':project, 'notices':notices, 'addnoticeform':addnoticeform}
    return render(request, 'project/noticeboard.html', payload)

@login_required
def todo(request, project_name):    
    """Allows to create a new todolist and todoitems."""
    project = get_project(request, project_name)
    lists = TodoList.objects.filter(user = request.user, project = project)
    addlistform = bforms.AddTodoListForm()
    if request.method == 'POST':
        if request.POST.has_key('addlist'):
            addlistform = bforms.AddTodoListForm(project, request.user, request.POST)
            if addlistform.is_valid():
                addlistform.save()
                return HttpResponseRedirect('.')
        elif request.POST.has_key('additem'):
            if request.POST['text']:
                id = int(request.POST['id'])
                list = TodoList.objects.get(id = id)
                item = TodoItem(list = list, text = request.POST['text'])
                item.save()
    if request.method == 'GET':
        addlistform = bforms.AddTodoListForm()
    payload = {'project':project, 'lists':lists, 'addlistform':addlistform}
    return render(request, 'project/todo.html', payload)

