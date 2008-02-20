from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms
from defaults import *
from django.core.paginator import ObjectPaginator, InvalidPage

import calendar as cal
import datetime

def index(request, project_name):
    project = get_project(request, project_name)
    interesting_months = project.get_interesting_months()
    month_data = []
    for month in interesting_months:
        month_datum = {}
        month_datum['name'] = datetime.date(month[0], month[1], month[2]).strftime('%B %y')
        month_datum['href'] = '/%s/calendar/%s/%s/' % (project.shortname, month[0], month[1])
        month_cal = cal.monthcalendar(month[0], month[1])
        flattened_dates = flatten(month_cal)
        start_tasks = project.task_start_dates_month(month[0], month[1])
        end_tasks = project.task_end_dates_month(month[0], month[1])
        start_dates_array = [[] for i in range(len(flattened_dates))]
        end_dates_array = [[] for i in range(len(flattened_dates))]
        for task in start_tasks:
            index = flattened_dates.index(task[0].day)
            start_dates_array[index].append(task[1])
        for task in end_tasks:
            index = flattened_dates.index(task[0].day)
            end_dates_array[index].append(task[1])
        d = zip(flattened_dates, start_dates_array, end_dates_array)
        month_datum['calendar'] = unflatten(d)
        month_data.append(month_datum)
    weekheader = cal.day_abbr
    payload = locals()
    return render(request, 'project/calendarindex.html', payload,)

def month_cal(request, project_name, year, month):
    project = get_project(request, project_name)
    year = int(year)
    month = int(month)
    interesting_months = project.get_interesting_months()
    month_data = []
    for month_ in interesting_months:
        month_datum = {}
        month_datum['name'] = datetime.date(month_[0], month_[1], month_[2]).strftime('%B %y')
        month_datum['href'] = '/%s/calendar/%s/%s/' % (project.shortname, month_[0], month_[1])
        month_data.append(month_datum)
    starting_tasks = Task.objects.filter(project = project, expected_start_date__year = year, expected_start_date__month = month)
    ending_tasks = Task.objects.filter(project = project, expected_end_date__year = year, expected_end_date__month = month)
    month_dates = cal.monthcalendar(year, month)
    flattened_dates = flatten(month_dates)
    start_dates_array = [[] for i in range(len(flattened_dates))]
    for task in starting_tasks:
        index = flattened_dates.index(task.expected_start_date.day)
        start_dates_array[index].append(task)
    end_dates_array = [[] for i in range(len(flattened_dates))]
    for task in ending_tasks:
        index = flattened_dates.index(task.expected_end_date.day)
        end_dates_array[index].append(task)
    
    d = zip(flattened_dates, start_dates_array, end_dates_array)
    month_dates = unflatten(d)
    weekheader = cal.day_name
    payload = locals()
    return render(request, 'project/calendar.html', payload,)

def flatten(arr):
    """flatten a 2d array."""
    flat = []
    for el in arr:
        flat.extend(el)
    return flat

def unflatten(arr):
    """Unflatten a calendar array flattened using flatten."""
    return [arr[7*i: 7*i+7] for i in range(len(arr)/7)]
    

def append_to_arr(arr, task):
    day = task.expected_start_date.day
    for i, el in enumerate(month_dates):
        for j, el2 in enumerate(month_dates[i]):
            if day == month_dates[i][j][0]:
                pass