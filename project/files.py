from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms
import time
import hmac
import sha
import base64
import secrets
import defaults

import S3

def files(request, project_name):
    """Files for a project. Shows the files uploaded for a project.
    Actions available:
    Add files:  Owner Participant
    """
    project = get_project(request, project_name)
    gen = S3.QueryStringAuthGenerator(secrets.aws_id, secrets.aws_key)
    print gen.list_bucket(defaults.bucket)
    """files = []
    for file in project.projectfile_set.all():
        url = gen.get(bucket, '/%s/%s' % (project.name, file.current_revision.get_name()))
        files.append((file, url))"""
        
    addfileform = bforms.AddFileForm(project = project, user = request.user)    
    aws_id = secrets.aws_id
    if request.method == 'POST':
        addfileform = bforms.AddFileForm(project , request.user, request.POST, request.FILES)
        if addfileform.is_valid():
            addfileform.save()
            return HttpResponseRedirect('.')
    payload = locals()
    return render(request, 'project/files.html', payload)
