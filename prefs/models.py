from django.db import models
from django.contrib.auth.models import User

startpage_choices = (
    ('Project Details', 'Project Details'),
    ('Tasks', 'Tasks'),
    ('Todos', 'Todos'),
    ('Wiki', 'Wiki'),
    ('Metrics', 'Metrics'),
)

class UserProfile(models.Model):
    user = models.ForeignKey(User)
    plain_ui = models.BooleanField(default = False)
    start_page = models.CharField(choices = startpage_choices, max_length = 100)
    
    
    
    
