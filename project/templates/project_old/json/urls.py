from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template

urlpatterns = patterns('project.foo',
    (r'index', direct_to_template, '')
    )                       