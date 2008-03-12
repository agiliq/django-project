from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as auth_login
from django.contrib.auth.views import logout as auth_logout
from django.contrib import auth
from django.conf import settings as settin
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
from prefs.models import *
import bforms

@login_required
def settings(request):
    profile = request.user.get_profile()
    prefform = bforms.PreferencesForm(instance = profile)
    
    if request.method == 'POST':
        prefform = bforms.PreferencesForm(instance = profile, data=request.POST)
        if prefform.is_valid():
            prefform.save()
            return HttpResponseRedirect('.')
    payload = {'prefform':prefform}
    return render(request, 'registration/settings.html', payload)


def login(request):
    """Login a user.
    Actions avialable:
    Login: Anyone"""
    #return auth_login(request)
    """Display and processs the login form."""
    no_cookies = False
    account_disabled = False
    invalid_login = False
    redirect_to = request.REQUEST.get('REDIRECT_FIELD_NAME', settin.LOGIN_REDIRECT_URL)
    
    if request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
            form = bforms.LoginForm(request.POST)
            if form.is_valid():
                user = auth.authenticate(username = form.cleaned_data['username'],
                                         password = form.cleaned_data['password'])
                if user:
                    if user.is_active:
                        print type(settin)
                        request.session[settin.PERSISTENT_SESSION_KEY] = form.cleaned_data['remember_user']
                        
                        auth.login(request, user)
                        # login successful, redirect
                        return HttpResponseRedirect(redirect_to)
                    else:
                        account_disabled = True
                else:
                    invalid_login = True
        else:
            no_cookies = True
            form = None
    else:
        form = bforms.LoginForm()
    
    # cookie must be successfully set/retrieved for the form to be processed    
    request.session.set_test_cookie()
    return render_to_response('registration/login.html', 
                              { 'no_cookies': no_cookies,
                                'account_disabled': account_disabled,
                                'invalid_login': invalid_login,
                                'form': form,
                                'REDIRECT_FIELD_NAME': redirect_to },
                              context_instance = RequestContext(request))    
    
def logout(request):
    """Logout a user.
    Actions available:
    Logout: Anyone"""
    return auth_logout(request, template_name='registration/logout.html')
    
def profile(request):
    """Show the profile for a user and allows to change settings."""
    user = request.user
    projects = [(sub.project, sub.group) for sub in user.subscribeduser_set.all()]
    if request.method == 'POST':
        shortname = request.POST['shortname']
        project = Project.objects.get(shortname = shortname)
        sub = SubscribedUser.objects.get(project = project, user = user)
        if sub.group == 'Owner':
            raise Exception('Cannot delete owner')
        else:
            sub.delete()
    elif request.method == 'GET':
        pass
    payload = {'projects':projects}
    return render(request, 'registration/profile.html', payload)
    
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