from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms

def wiki(request, project_name):
    """Shows recently created pages.
    Shows recently modified pages.
    Shows some blurb about the wiki.
    Allows creating a new page.
    """
    project = get_project(request, project_name)
    wikipages = WikiPage.objects.filter(project = project)
    payload = {'project':project,'wikipages':wikipages}
    return render(request, 'project/wiki.html', payload)

def wikipage(request, project_name, page_name):
    """Shows a specific wiki page.
    links to its history, edit the page
    """    
    pass

def create_wikipage(request, project_name, page_name=None):
    """Create a new wiki page."""
    project = get_project(request, project_name)
    if request.method == 'POST':
        wikiform = bforms.CreateWikiPageForm(project, request.user, request.POST)
        if wikiform.is_valid():
            wikiform.save()
            return HttpResponseRedirect('.')
    if request.method == 'GET':        
        wikiform = bforms.CreateWikiPageForm()
    payload = {'wikiform':wikiform}
    return render(request, 'project/wikicreate.html', payload)

def edit_wikipage(request, project_name, page_name=None):
    """Edit an existing wiki page."""
    pass


def wiki_revision(request, project_name, page_name, revision_id):
    """Shows revisions for a specific wiki page, and allows rolling back to any of its revisions."""
    pass
