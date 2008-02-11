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
    payload = {'project':project, 'wikipages':wikipages}
    return render(request, 'project/wiki.html', payload)

def wikipage(request, project_name, page_name):
    """Shows a specific wiki page.
    links to its history, edit the page
    """
    project = get_project(request, project_name)
    page = WikiPage.objects.get(name = page_name, project = project)
    payload = {'project':project, 'page':page}
    return render(request, 'project/wikipage.html', payload)

def create_wikipage(request, project_name, page_name=None):
    """Create a new wiki page."""
    project = get_project(request, project_name)
    if request.method == 'POST':
        wikiform = bforms.CreateWikiPageForm(project, request.user, request.POST)
        if wikiform.is_valid():
            page = wikiform.save()
            return HttpResponseRedirect(page.get_absolute_url())
    if request.method == 'GET':        
        wikiform = bforms.CreateWikiPageForm()
    payload = {'project':project, 'wikiform':wikiform}
    return render(request, 'project/wikicreate.html', payload)

def edit_wikipage(request, project_name, page_name=None):
    """Edit an existing wiki page."""
    project = get_project(request, project_name)
    page = WikiPage.objects.get(name = page_name, project = project)
    
    if request.method == 'POST':
        editform = bforms.EditWikiPageForm(request.user, page, request.POST)
        if editform.is_valid():
            editform.save()
            return HttpResponseRedirect(page.get_absolute_url())
    if request.method == 'GET':
        editform = bforms.EditWikiPageForm(request.user, page)
        
    payload = {'project':project, 'editform':editform}
    return render(request, 'project/wikiedit.html', payload)

def wiki_revision(request, project_name, page_name, revision_id):
    """Shows revisions for a specific wiki page, and allows rolling back to any of its revisions."""
    project = get_project(request, project_name)
    page = WikiPage.objects.get(name = page_name, project = project)
    revision = WikiPageRevision.objects.get(wiki_page = page, id = revision_id)
    if request.method == 'POST':
        """Rollback page to this revision."""
        from copy import copy
        newrevision = copy(revision)
        newrevision.id = None
        newrevision.save()
        newrevision.wiki_page.current_revision = newrevision
        newrevision.wiki_page.save()
        return HttpResponseRedirect('.')
    payload = {'project':project, 'page':page, 'revision':revision}
    return render(request, 'project/wikirevision.html', payload)
    
