from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms
from defaults import *
from django.core.paginator import ObjectPaginator, InvalidPage

def index(request):
    """If the user is not logged in, show him the login/register forms, with some blurb about the services. Else redirect to /dashboard/"""
    if request.user.is_authenticated():
        return HttpResponseRedirect('/dashboard/')
    register_form = bforms.UserCreationForm(prefix='register')
    payload = {'register_form':register_form, 'login_form':register_form}
    return render(request, 'project/index.html', payload)

@login_required
def dashboard(request):
    """The point of entry for a logged in user.
    Shows the available active projects for the user, and allows him to create one.
    Shows the pending invites to other projects.
    Shows very critical information about available projects.
    """
    user = request.user
    if request.GET.get('includeinactive', 0):
        subs = user.subscribeduser_set.all()
    else:
        subs = user.subscribeduser_set.filter(project__is_active = True)
    invites = user.inviteduser_set.filter(rejected = False)
    createform = bforms.CreateProjectForm()
    if request.method == 'POST':
        if request.POST.has_key('createproject'):
            createform = bforms.CreateProjectForm(user, request.POST)
            if createform.is_valid():
                createform.save()
                return HttpResponseRedirect('.')
        elif request.POST.has_key('acceptinv'):
            project = Project.objects.get(id = request.POST['projid'])
            invite = InvitedUser.objects.get(id = request.POST['invid'])
            subscribe = SubscribedUser(project = project, user = user, group = invite.group)
            subscribe.save()
            invite.delete()
            return HttpResponseRedirect('.')
        elif request.POST.has_key('activestatus'):
            print request.POST
            projid = request.POST['projectid']
            project = Project.objects.get(id = projid)
            if request.POST['activestatus'] == 'true':
                project.is_active = False
            elif request.POST['activestatus'] == 'false':
                project.is_active = True
            project.save()
            return HttpResponseRedirect('.')
            
    elif request.method == 'GET':
        createform = bforms.CreateProjectForm()
    
    payload = {'subs': subs, 'createform':createform, 'invites':invites}
    return render(request, 'project/dashboard.html', payload)

@login_required
def project_details(request, project_name):
    """
    Point of entry for a specific project.
    Shows the important information for a project.
    Shows form to invite an user.
    Form to create a new top task.
    Actions available here:
    Invite: Owner
    New Top Task: Owner Participant
    Mark Done: Owner Participant
    """
    user = request.user
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    inviteform = bforms.InviteUserForm()
    taskform = bforms.CreateTaskForm(project, user)
    new_tasks = project.new_tasks()
    new_tasks = project.new_tasks()
    overdue_tasks = project.overdue_tasks()
    if request.method == 'POST':
        if request.POST.has_key('invite'):
            if not (access == 'Owner'):
                return HttpResponseForbidden('%s(%s) does not have enough rights' % (request.user.username, access))
            inviteform = bforms.InviteUserForm(project, request.POST)
            if inviteform.is_valid():
                inviteform.save()
                return HttpResponseRedirect('.')
        elif request.POST.has_key('task'):
            if not (access in ('Owner', 'Participant')):
                return HttpResponseForbidden('%s(%s) does not have enough rights' % (request.user.username, access))
            taskform = bforms.CreateTaskForm(project, user, request.POST)
            if taskform.is_valid():
                taskform.save()
                return HttpResponseRedirect('.')
        elif request.POST.has_key('markdone') or request.POST.has_key('markundone'):
            if not (access in ('Owner', 'Participant')):
                return HttpResponseForbidden('%s(%s) does not have enough rights' % (request.user.username, access))
            if request.POST.has_key('xhr'):
                return handle_task_status(request, True)
            return handle_task_status(request)
        elif request.has_key('deletetask'):
            return delete_task(request)
            
    if request.method == 'GET':
        inviteform = bforms.InviteUserForm()
        taskform = bforms.CreateTaskForm(project, request.user)
    payload = {'project':project, 'inviteform':inviteform, 'taskform':taskform, 'new_tasks':new_tasks, 'overdue_tasks':overdue_tasks,}
    return render(request, 'project/projdetails.html', payload)


@login_required
def full_logs(request, project_name):
    """Shows the logs for a project.
    Actions available here:
    None"""
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    query_set = Log.objects.filter(project = project)
    logs, page_data = get_paged_objects(query_set, request, logs_per_page)
    payload = {'project':project, 'logs':logs, 'page_data':page_data}
    return render(request, 'project/fulllogs.html', payload)

@login_required
def noticeboard(request, project_name):
    """A noticeboard for the project.
    Shows the notices posted by the users.
    Shows the add notice form.
    Actions available here:
    Add a notice: Owner Participant Viewer (All)
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    query_set = Notice.objects.filter(project = project)
    notices, page_data = get_paged_objects(query_set, request, notices_per_page)
    if request.method == 'POST':
        addnoticeform = bforms.AddNoticeForm(project, request.user, request.POST)
        if addnoticeform.is_valid():
            addnoticeform.save()
            return HttpResponseRedirect('.')
    if request.method == 'GET':        
        addnoticeform = bforms.AddNoticeForm()
    payload = {'project':project, 'notices':notices, 'addnoticeform':addnoticeform, 'page_data':page_data}
    return render(request, 'project/noticeboard.html', payload)

@login_required
def todo(request, project_name):    
    """Allows to create a new todolist and todoitems.
    Actions available here:
    Add a todolist: Owner Participant
    Add a todoitem: Owner Participant
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    if request.GET.get('includecomplete', 0):
        lists = TodoList.objects.filter(user = request.user, project = project)
    else:
        lists = TodoList.objects.filter(user = request.user, project = project, is_complete_attr = False)
    addlistform = bforms.AddTodoListForm()
    if request.method == 'POST':
        if request.POST.has_key('addlist'):
            addlistform = bforms.AddTodoListForm(project, request.user, request.POST)
            if addlistform.is_valid():
                addlistform.save()
                return HttpResponseRedirect('.')
        elif request.POST.has_key('additem'):
            id = int(request.POST['id'])
            list = TodoList.objects.get(id = id)
            text_id = '%s-text'%list.id            
            if request.POST[text_id]:
                item = TodoItem(list = list, text = request.POST[text_id])
                item.save()
        elif request.POST.has_key('listmarkdone'):
            id = int(request.POST['id'])
            list = TodoList.objects.get(id = id)
            list.is_complete = True
            list.save()
            return HttpResponseRedirect('.')
        elif request.POST.has_key('itemmarkdone'):
            id = int(request.POST['id'])
            todoitem = TodoItem.objects.get(id = id)
            todoitem.is_complete = True
            todoitem.save()
            return HttpResponseRedirect('.')
            
    if request.method == 'GET':
        addlistform = bforms.AddTodoListForm()
    payload = {'project':project, 'lists':lists, 'addlistform':addlistform}
    return render(request, 'project/todo.html', payload)

def project_as_ul(request, project_name):
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    top_tasks = project.task_set.filter(parent_task__is_null = True)
    for task in top_task:
        pass

