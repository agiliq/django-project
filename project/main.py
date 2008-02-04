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

def project_details(request, project_name):
    pass



def full_logs(request, project_name):
    pass

def noticeboard(request, project_name):
    pass

def todo(request, project_name):    
    pass

