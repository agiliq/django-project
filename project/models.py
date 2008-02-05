from django.db import models
from django.contrib.auth.models import User
from django import newforms as forms

class AddTodoItemForm(forms.Form):
    text = forms.CharField()
    
    def __init__(self, list = None, *args, **kwargs):
        super(AddTodoItemForm, self).__init__(*args, ** kwargs)
        self.list = list
        
    def save(self):
        todoitem = TodoItem(text = self.cleaned_data['text'], list = self.user)
        todoitem.save()
        return todoitem

class Project(models.Model):
    """Model for project.
    shortname: Shortname, can not contain spaces , special chars. Used in url
    name: Name of the project
    owner: The user who has all the rights for the project.
    is_active: Is this project active?
    """
    shortname = models.CharField(max_length = 20)
    name = models.CharField(max_length = 200)
    owner = models.ForeignKey(User)
    is_active = models.BooleanField(default = True)
    created_on = models.DateTimeField(auto_now_add = 1)
    
    def get_absolute_url(self):
        return '/%s/' % self.shortname
    
    def __unicode__(self):
        return self.shortname
    
    def tasks_url(self):
        return '/%s/tasks/' % self.shortname
    
    def noticeboard_url(self):
        return '/%s/noticeboard/' % self.shortname
    
    def wiki_url(self):
        return '/%s/wiki/' % self.shortname
    
    def files_url(self):
        return '/%s/files/' % self.shortname
    
    def todo_url(self):
        return '/%s/todo/' % self.shortname
    
    def logs_url(self):
        return '/%s/logs/' % self.shortname
    
    class Admin:
        pass
    
options = (
        ('OWN', 'Owner'),
        ('PART', 'Participant'),
        ('VIEW', 'Viewer'),
    )
    
class SubscribedUser(models.Model):
    """Users who have access to a given project
    user: the user
    project: the project
    group: access rights"""
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    group = models.CharField(max_length = 20, choices = options)
    
    class Admin:
        pass    
    
class InvitedUser(models.Model):
    """Users who have invited to a given project
    user: the user
    project: the project
    group: access rights
    rejected: has the user rejected the invitation"""    
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    group = models.CharField(max_length = 20, choices = options)
    rejected = models.BooleanField(default = False)
    
    class Admin:
        pass    
    
class Task(models.Model):
    """Model for task.
    number: of the task under the current project.
    name: name for this task.
    project: the project under hwich this task was created.
    parent_task: For which task is this a subtask. If this is null, this is a task directly under project.
    user_responsible: who is the person who is responsible for completing this task.
    dates: excpected, and actual dates for this task.
    is_complete: has this task been completed? Defaults to false.
    created_on: when was this task created. Auto filled."""
    
    number = models.IntegerField()
    name = models.CharField(max_length = 200)
    project = models.ForeignKey(Project)
    parent_task = models.ForeignKey('Task', null = True)
    user_responsible = models.ForeignKey(User, null = True)
    expected_start_date = models.DateField()
    expected_end_date = models.DateField(null = True)
    actual_start_date = models.DateField(null = True)
    actual_end_date = models.DateField(null = True)
    is_complete = models.BooleanField(default = False)
    created_on = models.DateTimeField(auto_now_add = 1)
    #Versioning
    effective_start_date = models.DateTimeField(auto_now_add = True)
    effective_end_date = models.DateTimeField(null = True)
    version_number = models.IntegerField()
    is_current = models.BooleanField(default = True)
    
    def save(self):
        """If this is the firsts time populate required details, if this is update version it."""
        if not self.id:
            self.version_number = 1
            self.number = Task.objects.filter(project = self.project, is_current = True).count() + 1
            super(Task, self).save()
        else:
            #Version it
            import copy
            new_task = copy.copy(self)
            new_task.id = None
            new_task.save()
            
    def num_child_tasks(self):
        return self.task_set.all().count()
    
    def num_items(self):
        return self.taskitem_set.all().count()
    
    def get_absolute_url(self):
        return '/%s/taskdetails/%s/' % (self.project.shortname, self.number)
            
    class Admin:
        pass               

unit_choices = (
    ('HOUR', 'Hours'),
    ('DAY', 'Days'),
    ('MONTH', 'Months'),
    )    
class TaskItem(models.Model):
    """A task item for a task.
    number: of the task under the current project.
    name: name of the todo item.
    user: user who needs to do this todo.
    expected time: How much time this todo should take.
    actual_time: How much time this todo actually took.
    the unit in which you want to measure the time. Can be hours, days or months.
    is_complete: Has this todo item been completed.
    created_on: When was this todo created. AUto filled.
    """
    number = models.IntegerField()
    name = models.CharField(max_length = 200)
    task = models.ForeignKey(Task)
    user = models.ForeignKey(User, null = True)
    expected_time = models.DecimalField(decimal_places = 2, max_digits = 10)
    actual_time = models.DecimalField(decimal_places = 2, max_digits = 10, null = True)
    unit = models.CharField(max_length = 20, choices = unit_choices)
    is_complete = models.BooleanField(default = False)
    created_on = models.DateTimeField(auto_now_add = 1)
    #Versioning
    effective_start_date = models.DateTimeField(auto_now_add = 1)
    effective_end_date = models.DateTimeField(null = True)
    version_number = models.IntegerField()
    is_current = models.BooleanField(default = True)
    
    def save(self):
        """If this is the firsts time populate required details, if this is update version it."""
        if not self.id:
            self.version_number = 1
            self.number = TaskItem.objects.filter().count() + 1
            super(TaskItem, self).save()
        else:
            #Version it
            import copy
            new_task = copy.copy(self)
            new_task.id = None
            new_task.save()
            
    class Admin:
        pass
    
class TodoList(models.Model):
    """A todo list of a user of the project"""
    name = models.CharField(max_length = 200)
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    is_complete = models.BooleanField(default = False)
    created_on = models.DateTimeField(auto_now_add = 1)
    def get_item_form(self):
        return AddTodoItemForm()
    
    item_form = property(get_item_form, None, None)
    
    class Admin:
        pass
    
class TodoItem(models.Model):
    """A todo item of the project."""
    list = models.ForeignKey(TodoList)
    text = models.CharField(max_length = 200)
    is_complete = models.BooleanField(default = False)
    created_on = models.DateTimeField(auto_now_add = 1)
    
    class Admin:
        pass
    
class Log(models.Model):
    """Log of the project.
    project: Project for which this log is written.
    text: Text of the log.
    created_on: When was this log created."""
    project = models.ForeignKey(Project)
    text = models.CharField(max_length = 200)
    is_complete = models.BooleanField(default = False)
    created_on = models.DateTimeField(auto_now_add = 1)
    
class Notice(models.Model):
    """
    number: of the notice under the current project.
    user: User who wrote this notice.
    text: text of the notice.
    created_on: When was this notice created. Auto filled."""
    
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    text = models.TextField()
    created_on = models.DateTimeField(auto_now_add = 1)
    
    class Admin:
        pass
    
class WikiPage(models.Model):
    """Model of the wiki page.
    name: name of the page, should be alphanumeric. Shown in url.
    Title: title for the page. Can contain spaces.
    current_revion: the wiki_page which is the current revision for this page.
    created_on: When was this page created. Auto filled.
    """
    name = models.CharField(max_length = 20)
    title = models.CharField(max_length = 200)
    project = models.ForeignKey(Project)
    current_revision = models.ForeignKey('WikiPageRevision', null = True)
    created_on = models.DateTimeField(auto_now_add = 1)
    
class WikiPageRevision(models.Model):
    """user: The user who wrote this page revision.
    wiki_page: The page for which this revision is created.
    wiki_text: The text entered for this revion.
    html_text: The text converted to html.
    created_on: When was this revision created. Auto filled.
    """
    user = models.ForeignKey(User)
    wiki_page = models.ForeignKey(WikiPage)
    wiki_text = models.TextField()
    html_text = models.TextField()
    created_on = models.DateTimeField(auto_now_add = 1)
    
class TaskNotes(models.Model):
    """task_num: The task for which this note is created.
    We cant just use a foreign key coz, the note is for a specific task number, not a revision of it.
    """
    task_num = models.IntegerField()
    text = models.TextField()
    user = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now_add = 1)
    
class TodoNotes(models.Model):
    """task_num: The todo for which this note is created.
    We cant just use a foreign key coz, the note is for a specific todo number, not a revision of it.    
    """
    todo_num = models.IntegerField()
    text = models.TextField()
    user = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now_add = 1)    
    
    
class ProjectFile(models.Model):
    """project: The project for which this file is attached.
    file: the file."""
    project = models.ForeignKey(Project)
    file = models.FileField(upload_to = '/files/')

    
    

