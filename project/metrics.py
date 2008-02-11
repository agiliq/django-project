from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms

import pygooglechart

def project_health(request, project_name):
    project = get_project(request, project_name)
    num_tasks = project.task_set.filter(is_current = True).count()
    num_tasks_complete = project.task_set.filter(is_current = True, is_complete = True).count()
    users = project.subscribeduser_set.all()
    invitedusers = project.inviteduser_set.all()
    num_deadline_miss = project.num_deadline_miss()
    num_extra_hours = project.extra_hours()
    num_taskitems = project.num_taskitems()
    time = project.sum_time()
    time_complete = project.sum_time_complete()
    time_str = ''
    for el in time:
        time_str += '%s %s, ' % (el[1], el[0])
    time_str_complete = ''
    for el in time_complete:
        time_str_complete += '%s %s, ' % (el[1], el[0])
    if not time_str_complete:
        time_str_complete = 'no'
    start_month = project.start_month()
    end_month = project.end_month()
    project.user_timeload()
    #data for charts
    width = 200
    height = 70
    #CHarting
    task_chart = pygooglechart.PieChart2D(width, height)
    task_chart.add_data([num_tasks-num_tasks_complete, num_tasks_complete])
    task_chart.set_pie_labels(['In progress', 'Complete'])
    task_chart_url = task_chart.get_url()
    
    deadl_chart = pygooglechart.PieChart2D(width, height)
    deadl_chart.add_data([num_tasks - num_deadline_miss, num_deadline_miss])
    deadl_chart.set_pie_labels(['Others', 'Deadline missees'])
    deadl_chart_url = deadl_chart.get_url()
    
    item_chart = pygooglechart.PieChart2D(width, height)
    item_chart.add_data([num_taskitems - num_extra_hours, num_extra_hours])
    item_chart.set_pie_labels(['Others', 'Tasks with exta hours'])
    item_chart_url = item_chart.get_url()
    
    payload = locals()
    return render(request, 'project/projecthealth.html', payload)

def user_stats(request, project_name):
    pass
