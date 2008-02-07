from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as auth_login
from django.contrib.auth.views import logout as auth_logout

from helpers import *
from models import *
import bforms


def login(request):
    return auth_login(request)
    
def logout(request):
    return auth_logout(request, template_name='registration/logout.html')
    
def profile(request):
    pass
    
def register(request):
    if request.method == 'POST':
        form = bforms.UserCreationForm(request.POST)
        if form.is_valid():
            print form.save()
            return HttpResponseRedirect('/accounts/login/')
    if request.method == 'GET':
        form = bforms.UserCreationForm()
    payload = {'form':form}
    return render(request, 'registration/create_user.html', payload)