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
    bucket = 'i-love-foobar'
    project = get_project(request, project_name)
    """gen = S3.QueryStringAuthGenerator(secrets.aws_id, secrets.aws_key)
    files = []
    for file in project.projectfile_set.all():
        url = gen.get(bucket, '/%s/%s' % (project.name, file.current_revision.get_name()))
        files.append((file, url))"""
    addfileform = bforms.AddFileForm()    
    aws_id = secrets.aws_id
    if request.method == 'POST':
        addfileform = bforms.AddFileForm(request.POST, request.FILES)
        if addfileform.is_valid():
            conn = S3.AWSAuthConnection(secrets.aws_id, secrets.aws_key)
            filename = '/%s/%s' % (project, addfileform.cleaned_data['filename'].filename)
            try:
                old_file = project.projectfile_set.get(filename = addfileform.cleaned_data['filename'].filename)
                versions = old_file.projectfileversion_set.all().count()
                filename = '%s-%s' % (filename, versions + 1)
                response = conn.put(bucket, filename, addfileform.cleaned_data['filename'].content)
                saved_file = old_file
                saved_file_revision = ProjectFileVersion(file = saved_file, user = request.user, size = len(addfileform.cleaned_data['filename'].content))
                saved_file_revision.save()
                saved_file.current_revision = saved_file_revision
                saved_file.total_size += saved_file_revision.size
                saved_file.save()
            except ProjectFile.DoesNotExist, e:
                filename = '%s-%s' % (filename, 1)
                response = conn.put(bucket, filename, addfileform.cleaned_data['filename'].content)
                saved_file = ProjectFile(project = project, filename = addfileform.cleaned_data['filename'].filename, total_size = 0)
                saved_file.save()
                saved_file_revision = ProjectFileVersion(file = saved_file, user = request.user, size = len(addfileform.cleaned_data['filename'].content))
                saved_file_revision.save()
                saved_file.current_revision = saved_file_revision
                saved_file.total_size = saved_file_revision.size
                saved_file.save()
            return HttpResponseRedirect('.')
    payload = locals()
    return render(request, 'project/files.html', payload)
