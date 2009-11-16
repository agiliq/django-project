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

@login_required
def files(request, project_name):
    """Files for a project. Shows the files uploaded for a project.
    Actions available:
    Add files:  Owner Participant
    """
    project = get_project(request, project_name)
    gen = S3.QueryStringAuthGenerator(secrets.AWS_ID, secrets.AWS_SECRET_KEY)
    addfileform = bforms.AddFileForm(project = project, user = request.user)    
    if request.method == 'POST':
        if request.POST.has_key('Addfile'):
            addfileform = bforms.AddFileForm(project , request.user, request.POST, request.FILES)
            if addfileform.is_valid():
                addfileform.save()
                return HttpResponseRedirect('.')
        if request.POST.has_key('fileid'):
            fileid = int(request.POST['fileid'])
            file = ProjectFile.objects.get(project = project, id = fileid)
            conn = S3.AWSAuthConnection(secrets.AWS_ID, secrets.AWS_SECRET_KEY)
            for revision in file.projectfileversion_set.all():
                conn.delete(defaults.bucket, revision.revision_name)
            file.delete()
    payload = locals()
    return render(request, 'project/files.html', payload)
