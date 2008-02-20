from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms

def files(request, project_name):
    project = get_project(request, project_name)
    addfileform = bforms.AddFileForm()
    if request.method == 'POST':
        pass
    payload = {'project':project, 'addfileform':addfileform}
    return render(request, 'project/files.html', payload)
