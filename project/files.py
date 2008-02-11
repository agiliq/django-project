from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms

def files(request, project_name):
    project = get_project(request, project_name)
    payload = {'project':project}
    return render(request, 'project/files.html', payload)
