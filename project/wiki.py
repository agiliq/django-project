def wiki(request, project_name):
    """Shows recently created pages.
    Shows recently modified pages.
    Shows some blurb about the wiki.
    Allows creating a new page.
    """
    pass

def wikipage(request, project_name, page_name):
    """Shows a specific wiki page.
    links to its history, edit the page
    """    
    pass

def create_wikipage(request, project_name, page_name=None):
    """Create a new wiki page."""
    pass


def edit_wikipage(request, project_name, page_name=None):
    """Edit an existing wiki page."""
    pass


def wiki_revision(request, project_name, page_name, revision_id):
    """Shows revisions for a specific wiki page, and allows rolling back to any of its revisions."""
    pass
