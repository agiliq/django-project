from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

startpage_choices = (
    ('Project Details', 'Project Details'),
    ('Tasks', 'Tasks'),
    ('Todos', 'Todos'),
    ('Wiki', 'Wiki'),
    ('Metrics', 'Metrics'),
    ('Logs', 'Logs'),
)

class Template(models.Model):
    name = models.CharField(max_length = 100)
    
    class Admin:
        pass

class UserProfile(models.Model):
    user = models.ForeignKey(User)
    plain_ui = models.BooleanField(default = False)
    # template_name = models.ForeignKey(Template)
    start_page = models.CharField(choices = startpage_choices, max_length = 100)
    
    class Admin:
        pass
    
    
def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = UserProfile.objects.get_or_create(user=instance)  
 
post_save.connect(create_user_profile, sender=User) 
 
User.profile = property(lambda u: u.get_profile() )