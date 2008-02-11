from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms

def project_health(request, project_name):
    project = get_project(request, project_name)
    num_tasks = project.task_set.filter(is_current = True).count()
    num_tasks_complete = project.task_set.filter(is_current = True, is_complete = True).count()
    users = project.subscribeduser_set.all()
    invitedusers = project.inviteduser_set.all()
    project.num_deadline_miss()
    project.extra_hours()
    payload = locals()
    return render(request, 'project/projecthealth.html', payload)

def user_stats(request, project_name):
    pass
