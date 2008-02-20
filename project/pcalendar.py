from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms
from defaults import *
from django.core.paginator import ObjectPaginator, InvalidPage

import calendar as cal

def month_cal(request, project_name, year, month):
    year = int(year)
    month = int(month)
    starting_tasks = Task.objects.filter(expected_start_date__year = year, expected_start_date__month = month)
    ending_tasks = Task.objects.filter(expected_end_date__year = year, expected_end_date__month = month)
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
    """for i, el in enumerate(month_dates):
        for j, el2 in enumerate(month_dates[i]):
            month_dates[i][j] = [month_dates[i][j]]"""
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