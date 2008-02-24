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
    gen = S3.QueryStringAuthGenerator(secrets.aws_id, secrets.aws_key)
    files = []
    for file in project.projectfile_set.all():
        url = gen.get(bucket, '/%s/%s' % (project.name, file.filename))
        files.append((file, url))
    print files
    addfileform = bforms.AddFileForm()
    key_prefix = '/%s/' % project.shortname
    success_action_redirect = '/dashboard/'
    policy = """{
  "expiration": "%s",
  "conditions": [
    {"bucket": "i-love-foobar" },
    {"acl": "private" },
    {"success_action_redirect":"%s"},
    ["starts-with", "$key", "%s"],
  ]
}""" % (time.strftime('%Y-%m-%dT%I:%M:%S.000Z', time.gmtime((time.time() + defaults.expires_in))), success_action_redirect, key_prefix)
    #2009-01-01T12:00:00.000Z
    
    policy64 = base64.encodestring(policy).strip()
    policy64 = "".join(policy64.split())
    signature = base64.encodestring(hmac.new(secrets.aws_key, policy64, sha).digest()).strip()
    #policy64 = "ewogICJleHBpcmF0aW9uIjogIjIwMDktMDEtMDFUMTI6MDA6MDAuMDAwWiIsCiAgImNvbmRpdGlvbnMiOiBbCiAgICB7ImJ1Y2tldCI6ICJpLWxvdmUtZm9vYmFyIiB9LAogICAgeyJhY2wiOiAicHJpdmF0ZSIgfSwKICAgIFsic3RhcnRzLXdpdGgiLCAiJGtleSIsICIiXSwKICBdCn0K"
    #signature = "MWNT0ij61+0UIikEt9ngZI1LQbU="
    
    aws_id = secrets.aws_id
    if request.method == 'POST':
        addfileform = bforms.AddFileForm(request.POST, request.FILES)
        if addfileform.is_valid():
            #addfileform.cleaned_data['filename'].content
            conn = S3.AWSAuthConnection(secrets.aws_id, secrets.aws_key)
            filename = '/%s/%s' % (project, addfileform.cleaned_data['filename'].filename)
            response = conn.put(bucket, filename, addfileform.cleaned_data['filename'].content)
            saved_file = ProjectFile(project = project, filename = addfileform.cleaned_data['filename'].filename, user = request.user)
            saved_file.save()
            return HttpResponseRedirect('.')
    payload = locals()
    return render(request, 'project/files.html', payload)

    """policy641 = "ewogICJleHBpcmF0aW9uIjogIjIwMDktMDEtMDFUMTI6MDA6MDAuMDAwWiIsCiAgImNvbmRpdGlvbnMiOiBbCiAgICB7ImJ1Y2tldCI6ICJpLWxvdmUtZm9vYmFyIiB9LAogICAgeyJhY2wiOiAicHJpdmF0ZSIgfSwKICAgIFsic3RhcnRzLXdpdGgiLCAiJGtleSIsICIiXSwKICBdCn0="
    print policy64
    print policy641
    print policy641 == policy642
    app = diff_match_patch.diff_match_patch()
    print app.diff_main(policy641, policy642)"""
