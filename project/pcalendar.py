"""from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from helpers import *
from models import *
import bforms
from defaults import *
from django.core.paginator import ObjectPaginator, InvalidPage"""

import calendar as cal

def index(request, project_name):
    print dir(cal)
    month = cal.monthcalendar(2008, 2)
    payload = locals()
    return render(request, 'project/calendar.html', payload,)