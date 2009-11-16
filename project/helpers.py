from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from django.http import HttpResponseRedirect, HttpResponse
import csv

from django.core.paginator import Paginator, InvalidPage
from django.template.loader import get_template
from django.template import Context
import StringIO
import sx.pisa3 as pisa
import defaults

import BeautifulSoup as soup
from models import *

def get_project(request, project_name):
    """Returns the project with the given name if the logged in user has access to the project. Raises 404 otherwise."""
    try:
        project = Project.objects.get(shortname = project_name)
    except Project.DoesNotExist:
        raise Http404
    try:
        project.subscribeduser_set.get(user = request.user)
    except SubscribedUser.DoesNotExist:
        raise Http404
    return project

def get_access(project, user):
    """Returns the access of the user passed for the project passed."""
    return SubscribedUser.objects.get(project = project, user = user).group

def render(request, template, payload):
    """This populates the site wide template context in the payload passed to the template.
        It the job of this methods to make sure that, if user want to see the PDF they are able to see it.
    """
    if request.GET.get('pdf', ''):
        tarr = template.split('/')
        template = '%s/%s/%s' % (tarr[0], 'pdf', tarr[1])
        template = get_template(template)
        html = template.render(Context(payload))
        import copy
        hsoup = soup.BeautifulSoup(html)
        links = hsoup.findAll('a')
        for link in links:
            if not link['href'].startswith('http'):
                link['href'] = '%s%s' % (defaults.base_url, link['href'])
        html = StringIO.StringIO(str(hsoup))
        result = StringIO.StringIO()
        pdf = pisa.CreatePDF(html, result)
        if pdf.err:
            return HttpResponse(pdf.log)
        return HttpResponse(result.getvalue(), mimetype='application/pdf')
    if not payload.get('subs', ''):
        try:
            subs = request.user.subscribeduser_set.all()
            payload.update({'subs':subs})
        except AttributeError, e:
            pass
    #Populate the PDF path
    if request.META['QUERY_STRING']:
        pdfpath = '%s&pdf=1' % request.get_full_path()
    else:
        pdfpath = '%s?pdf=1'% request.get_full_path()
    payload.update({'pdfpath':pdfpath})
    return render_to_response(template, payload, RequestContext(request))

def get_pagination_data(obj_page, page_num):
    data = {}
    page_num = int(page_num)
    data['has_next_page'] = obj_page.has_next_page(page_num)
    data['next_page'] = page_num + 1
    data['has_prev_page'] = obj_page.has_previous_page(page_num)
    data['prev_page'] = page_num - 1
    data['first_on_page'] = obj_page.first_on_page(page_num)
    data['last_on_page'] = obj_page.last_on_page(page_num)
    data['total'] = obj_page.hits
    return data

def get_paged_objects(query_set, request, obj_per_page):
    try:
        page = request.GET['page']
        page = int(page)
    except KeyError, e:
        page = 0
    object_page = ObjectPaginator(query_set, obj_per_page)
    object = object_page.get_page(page)
    page_data = get_pagination_data(object_page, page)
    return object, page_data

def handle_task_status(request, is_xhr = False):
    """Handle changes to status for a task. (Is_complete status toggle)."""
    id = request.POST['taskid']
    task = Task.objects.get(id = id)
    if request.POST.has_key('markdone'):
        task.is_complete_prop = True
    else:
        task.is_complete_prop = False
    task.save()
    if is_xhr:
        return task.id
    return HttpResponseRedirect('.')

def handle_taskitem_status(request):
    """Handle changes to status for a taskitem. (Is_complete status toggle)."""
    id = request.POST['taskitemid']
    taskitem = TaskItem.objects.get(id = id)
    if request.POST.has_key('itemmarkdone'):
        taskitem.is_complete = True
    else:
        taskitem.is_complete = False
    taskitem.save()
    return HttpResponseRedirect('.')

def delete_task(request):
    """Delete a task."""
    taskid = request.POST['taskid']
    task = Task.objects.get(id = taskid)
    task.delete()
    return HttpResponseRedirect('.')

def reponse_for_cvs(filename = 'filename.csv', project=None):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    writer = csv.writer(response)
    if project:
        writer.writerow(Project.as_csv_header())
        writer.writerow(project.as_csv())
        writer.writerow(())        
    return response, writer
