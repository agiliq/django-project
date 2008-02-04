from django import newforms as forms
from django.newforms import ValidationError
import re

from models import *

class CreateProjectForm(forms.Form):
    shortname = forms.CharField(max_length = 20)
    name = forms.CharField(max_length = 200)
    
    def __init__(self, user = None, *args, **kwargs):
        super(CreateProjectForm, self).__init__(*args, **kwargs)
        self.user = user
    
    def save(self):
        project = Project(name = self.cleaned_data['name'], shortname=self.cleaned_data['shortname'])
        project.owner = self.user
        project.save()
        subscribe = SubscribedUser(user = self.user, project = project, group = 'OWN')
        subscribe.save()
        return project
    
    def clean_shortname(self):
        alnum_re = re.compile(r'^\w+$')
        if not alnum_re.search(self.cleaned_data['shortname']):
            raise ValidationError("This value must contain only letters, numbers and underscores.")
        self.is_valid_shortname()
        return self.cleaned_data['shortname']
    
    def is_valid_shortname(self):
        try:
            Project.objects.get(shortname = self.cleaned_data['shortname'])
        except Project.DoesNotExist:
            return
        raise ValidationError('This project name is already taken. Please try another.')
