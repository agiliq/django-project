from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms

def files(request, project_name):
    """Files for a project. Shows the files uploaded for a project.
    Actions available:
    Add files:  Owner Participant
    """
    project = get_project(request, project_name)
    addfileform = bforms.AddFileForm()
    if request.method == 'POST':
        pass
    payload = {'project':project, 'addfileform':addfileform}
    return render(request, 'project/files.html', payload)
