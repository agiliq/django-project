from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms
import diff_match_patch
from html2text import html2text

def wiki(request, project_name):
    """Shows recently created pages.
    Shows recently modified pages.
    Shows some blurb about the wiki.
    Actions available here:
    None
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    wikipages = WikiPage.objects.filter(project = project)
    payload = {'project':project, 'wikipages':wikipages}
    return render(request, 'project/wiki.html', payload)

def wikipage(request, project_name, page_name):
    """Shows a specific wiki page.
    links to its history, edit the page
    Actions available here: None
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    page = WikiPage.objects.get(name = page_name, project = project)
    payload = {'project':project, 'page':page}
    return render(request, 'project/wikipage.html', payload)

def create_wikipage(request, project_name, page_name=None):
    """Create a new wiki page.
    Actions available here:
    Create a wiki page:  Owner Participant"""
    project = get_project(request, project_name)
    access = get_access(project, request.user)
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
    """Edit an existing wiki page.
    Actions available here.
    Edit an existing page:  Owner Participant"""
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    page = WikiPage.objects.get(name = page_name, project = project)
    
    if request.method == 'POST':
        editform = bforms.EditWikiPageForm(request.user, page, request.POST)
        if editform.is_valid():
            editform.save()
            return HttpResponseRedirect(page.get_absolute_url())
    if request.method == 'GET':
        editform = bforms.EditWikiPageForm(request.user, page)
        
    payload = {'project':project, 'editform':editform, 'page':page}
    return render(request, 'project/wikiedit.html', payload)

def wiki_revision(request, project_name, page_name, revision_id):
    """Shows revisions for a specific wiki page, and allows rolling back to any of its revisions.
    Actions available here:
    Roll back page to a specific revision.  Owner Participant
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
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
        return HttpResponseRedirect(newrevision.wiki_page.get_absolute_url())
    if request.method == 'GET':
        pass
    payload = {'project':project, 'page':page, 'revision':revision}
    return render(request, 'project/wikirevision.html', payload)

def wikipage_diff(request, project_name, page_name):
    """Shows previous versions and summary about them.
    Actions available here:
    Allows to do a diff between two versions:  Owner Participant Viewer
    """
    project = get_project(request, project_name)
    access = get_access(project, request.user)
    page = WikiPage.objects.get(name = page_name, project = project)
    version1 = int(request.GET.get('version1', 0))
    version2 = int(request.GET.get('version2', 0))
    if version1 and version2:
        rev1 = WikiPageRevision.objects.get(wiki_page = page, id = version1)
        rev2 = WikiPageRevision.objects.get(wiki_page = page, id = version2)
        print rev1.id
        print rev1.wiki_page
        print 111, rev1.html_text
        print 111, rev1.wiki_text
        app = diff_match_patch.diff_match_patch()
        diff = app.diff_main(html2text(rev1.html_text), html2text(rev2.html_text))
        app.diff_cleanupSemantic(diff)
        htmldiff = app.diff_prettyHtml(diff)
        payload = {'project':project, 'page':page, 'revision1':rev1, 'revision2':rev2, 'htmldiff': htmldiff}
        return render(request, 'project/wikidiffresult.html', payload)
    else:
        payload = {'project':project, 'page':page,}
        return render(request, 'project/wikidiff.html', payload)
    
