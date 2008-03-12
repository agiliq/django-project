from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms
from defaults import *
from django.core.paginator import ObjectPaginator, InvalidPage
import csv
import StringIO
import sx.pisa3 as pisa

def index(request):
    """If the user is not logged in, show him the login/register forms, with some blurb about the services. Else redirect to /dashboard/"""
    if request.user.is_authenticated():
        return HttpResponseRedirect('/dashboard/')
    if request.method == 'POST':
        return login(request)
    register_form = bforms.UserCreationForm(prefix='register')
    login_form = form = bforms.LoginForm()
    payload = {'register_form':register_form, 'login_form':login_form}
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
        print request.POST
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
    if request.GET.get('csv', ''):
        response, writer = reponse_for_cvs()
        writer.writerow(('Project',))
        for sub in subs:
            writer.writerow((sub.project.name, ))
        writer.writerow(())        
        writer.writerow(('Project', 'Task Name', 'Due On'))
        for sub in subs:
            for task in sub.project.overdue_tasks():
                writer.writerow((task.project.name, task.name, task.expected_end_date))
        return response
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
                print request.POST
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
        
    if request.GET.get('csv', ''):
        response, writer = reponse_for_cvs()
        writer.writerow(Project.as_csv_header())
        writer.writerow(project.as_csv())
        writer.writerow(())
        writer.writerow(Task.as_csv_header())
        for task in new_tasks:
            writer.writerow(task.as_csv())
        writer.writerow(())    
        writer.writerow(Task.as_csv_header())
        for task in overdue_tasks:
            writer.writerow(task.as_csv())
        return response
    
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
    if request.GET.get('csv', ''):
        response, writer = reponse_for_cvs(project=project)
        writer.writerow((Log.as_csv_header()))
        for log in query_set:
            writer.writerow((log.as_csv()))
        return response
        
    payload = {'project':project, 'logs':logs, 'page_data':page_data}
    return render(request, 'project/fulllogs.html', payload)

@login_required
def settings(request, project_name):
    """Allows settings site sepcific settings."""
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    if not (access == 'Owner'):
        return HttpResponseForbidden('%s(%s) does not have enough rights' % (request.user.username, access))    
    if request.method == 'POST':
        if request.POST.get('remove', ''):
            username = request.POST['user']
            sub = SubscribedUser.objects.get(project__shortname = project_name, user__username = username)
            sub.delete()
            return HttpResponseRedirect('.')
        if request.POST.get('chgroup', ''):
            username = request.POST['user']
            sub = SubscribedUser.objects.get(project__shortname = project_name, user__username = username)
            sub.group = request.POST['group']
            sub.save()
            return HttpResponseRedirect('.')
    payload = {'project':project}
    return render(request, 'project/settings.html', payload)

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
    if request.GET.get('csv', ''):
        response, writer = reponse_for_cvs(project=project)
        writer.writerow(Notice.as_csv_header())
        for notice in query_set:
            writer.writerow(notice.as_csv())
        return response
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
        
    if request.GET.get('csv', ''):
        response, writer = reponse_for_cvs(project=project)
        writer.writerow(('Todo Lists',))
        writer.writerow(TodoList.as_csv_header())
        lists = TodoList.objects.filter(user = request.user, project = project)
        for list in lists:
            writer.writerow(list.as_csv())
        for list in lists:
            for item in list.todoitem_set.all():
                writer.writerow(item.as_csv())
        return response
    payload = {'project':project, 'lists':lists, 'addlistform':addlistform}
    return render(request, 'project/todo.html', payload)


def project_as_ul(request, project_name):
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    top_tasks = project.task_set.filter(parent_task__is_null = True)
    for task in top_task:
        pass
    


