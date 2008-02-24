from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as auth_login
from django.contrib.auth.views import logout as auth_logout

from helpers import *
from models import *
import bforms


def login(request):
    """Login a user.
    Actions avialable:
    Login: Anyone"""
    return auth_login(request)
    
def logout(request):
    """Logout a user.
    Actions available:
    Logout: Anyone"""
    return auth_logout(request, template_name='registration/logout.html')
    
def profile(request):
    """Show the profile for a user."""
    pass
    
def register(request):
    """Register a new user.
    Actions available:
    Register: Anyone
    """
    if request.method == 'POST':
        form = bforms.UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/accounts/login/')
    if request.method == 'GET':
        form = bforms.UserCreationForm()
    payload = {'form':form}
    return render(request, 'registration/create_user.html', payload)

def user_details(request, project_name, username):
    """Shows the details for a user. (Pening tasks/taskitems)."""
    project = get_project(request, project_name)
    user = User.objects.get(username = username)
    timeload = project.user_timeload_sp(user)
    tasks_count = project.user_tasks_sp(user)
    show_complete =  request.GET.get('includecomplete', 0)
    if show_complete:
        tasks = project.task_set.filter(user_responsible = user)
        items = project.taskitem_set.filter(user = user)
    else:
        tasks = project.task_set.filter(user_responsible = user, is_complete = False)
        items = project.taskitem_set.filter(user = user, is_complete = False)
    if request.POST.has_key('markdone') or request.POST.has_key('markundone'):
        if request.POST.has_key('xhr'):
            return handle_task_status(request, True)
        return handle_task_status(request)
    payload = locals()
    return render(request, 'project/userdetails.html', payload)