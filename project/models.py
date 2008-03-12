from django.db import models
from django.contrib.auth.models import User
from django import newforms as forms
import datetime

from dojofields import *
from django.db import connection
import re

import time
import mptt

class AddTodoItemForm(forms.Form):
    """A form to add a todo item to a todo list."""
    text = DojoCharField()
    
    def __init__(self, list = None, *args, **kwargs):
        kwargs.update({'prefix':list.id})
        super(AddTodoItemForm, self).__init__(*args, ** kwargs)
        self.list = list
        
    def save(self):
        todoitem = TodoItem(text = self.cleaned_data['text'], list = self.user)
        todoitem.save()
        
        
        return todoitem
    
class MarkDoneForm(forms.Form):
    """A form to mark the task as done."""
    is_complete = forms.BooleanField()
    
    def __init__(self, task, *args, **kwargs):
        kwargs.update({'prefix':task.id})
        super(MarkDoneForm, self).super(*args, **kwargs)
        self.task = task
        self.fields['is_complete'].initial = task.is_complete
    
    def save(self):
        pass

class Project(models.Model):
    """Model for project.
    shortname: Shortname, can not contain spaces , special chars. Used in url
    name: Name of the project
    owner: The user who has all the rights for the project.
    start_date: When does this project start?
    end_date: When does this project end?
    is_active: Is this project active?
    """
    shortname = models.CharField(max_length = 20, unique = True)
    name = models.CharField(max_length = 200)
    owner = models.ForeignKey(User)
    start_date = models.DateField()
    end_date = models.DateField(null = True)
    is_active = models.BooleanField(default = True)
    created_on = models.DateTimeField(auto_now_add = 1)
    
    def validate(self):
        """Validations for project.
        1. Short name must contain aplhnum only.
        2. Shortname must not be empy
        3. Name must not be empty.
        """
        if self.name == '':
            raise Exception('name can not be an empty string.')
        if self.shortname == '':
            raise Exception('shortname can not be an emplty string.')
        alnum_re = re.compile(r'^\w+$')
        if not alnum_re.search(self.shortname):
            raise Exception("This value must contain only letters, numbers and underscores.")
        
    def save(self):
        self.validate()
        super(Project, self).save()
        
    @classmethod
    def as_csv_header(self):
        return ('Shortname', 'Name', 'Owner', 'Start Date', 'End Date')
        
    def as_csv(self):
        return (self.shortname, self.name, self.owner, self.start_date, self.end_date)
        
    def __unicode__(self):
        return self.shortname
    
    def get_absolute_url(self):
        """Tte absolute url for project."""
        return '/%s/' % self.shortname
    
    def tasks_url(self):
        """Url to the tasks page."""
        return '/%s/tasks/' % self.shortname
    
    def quicktasks_url(self):
        """Url to the tasks quick entry page."""
        return '/%s/tasks/quickentry/' % self.shortname
    
    def quicktaskitems_url(self):
        """Url to the tasks quick entry page."""
        return '/%s/taskitems/quickentry/' % self.shortname
    
    def noticeboard_url(self):
        """Urls to the noticeboard."""
        return '/%s/noticeboard/' % self.shortname
    
    def wiki_url(self):
        """Url to the project wiki."""
        return '/%s/wiki/' % self.shortname
    
    def new_wikipage_url(self):
        """Url to create a new wiki page."""
        return '/%s/wiki/new/' % self.shortname
    
    def files_url(self):
        """Url to files page."""
        return '/%s/files/' % self.shortname
    
    def todo_url(self):
        """Url to the todo page."""
        return '/%s/todo/' % self.shortname
    
    def calendar_url(self):
        """Url to the calendars page."""
        return '/%s/calendar/' % self.shortname
    
    
    def metrics_url(self):
        """Url to the metrics page."""
        return '/%s/health/' % self.shortname
    
    def logs_url(self):
        """Url to the logs page."""
        return '/%s/logs/' % self.shortname
    
    def feed_url(self):
        """Url to the rss for this project."""
        return '/feeds/project/%s/' % self.shortname
    
    def get_last_date(self):
        """Returns a reasonable last date even if the end date for the project is null."""
        cursor = connection.cursor()
        stmt = 'SELECT ifnull( ifnull( end_date, max( project_task.expected_end_date ) ) , adddate( curdate( ) , 30 ) ) FROM project_project LEFT JOIN project_task ON project_project.id = project_task.project_id WHERE project_project.id = %s' % self.id
        cursor.execute(stmt)
        data = cursor.fetchone()
        return data[0]
    
    def get_interesting_months(self):
        """Get interesting months for this project. Interesting months are those month in which either a task started or a task ended."""
        cursor = connection.cursor()
        stmt = 'SELECT DISTINCT year( expected_start_date ) , month( expected_start_date ), 1 FROM project_task UNION SELECT DISTINCT year( expected_end_date ) , month( expected_end_date ), 1 FROM project_project, project_task WHERE project_project.id = project_task.project_id AND project_project.id = %s' % self.id
        cursor.execute(stmt)
        data = cursor.fetchall()
        print data
        print stmt
        return data
    
    def new_tasks(self):
        """Shows the three recemtly created tasks."""
        return self.task_set.all().order_by('-created_on')[:3]
    
    def overdue_tasks(self):
        """Shows all the tasks which are over due."""
        return self.task_set.filter(expected_end_date__lt = datetime.datetime.today(), is_complete = False)
    
    def invited_users(self):
        """Shows the users which have been invited, but have not accepted the invitation."""
        return self.inviteduser_set.all()
    
    def num_deadline_miss(self):
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(id) FROM project_task WHERE expected_end_date < actual_end_date AND project_id = %s AND is_current = %s' % (self.id, True))
        data = cursor.fetchone()
        return data[0]
    
    def extra_hours(self):
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(project_taskitem.id) FROM project_task, project_taskitem WHERE project_task.number = project_taskitem.task_num AND project_taskitem.expected_time < project_taskitem.actual_time AND project_task.project_id = %s AND project_taskitem.is_current = %s AND project_task.is_current = %s' % (self.id, True, True))
        data = cursor.fetchone()
        return data[0]
    
    def num_taskitems(self):
        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(project_taskitem.id) FROM project_task, project_taskitem WHERE project_task.number = project_taskitem.task_num AND project_task.project_id = %s AND project_taskitem.is_current = %s  AND project_task.is_current = %s' % (self.id, True, True))
        data = cursor.fetchone()
        return data[0]
        #return self.taskitem_set.all().count()
    
    def sum_time(self):
        cursor = connection.cursor()
        stmt = 'SELECT unit, sum(CASE WHEN project_taskitem.actual_time IS NULL THEN project_taskitem.expected_time ELSE project_taskitem.actual_time END) FROM project_task, project_taskitem WHERE project_task.number = project_taskitem.task_num AND project_task.project_id = %s AND project_taskitem.is_current = %s  AND project_task.is_current = %s GROUP BY unit' % (self.id, True, True)
        print stmt
        cursor.execute(stmt)
        data = cursor.fetchall()
        return data
    
    def sum_time_complete(self):
        cursor = connection.cursor()
        cursor.execute('SELECT unit, sum(CASE WHEN project_taskitem.actual_time IS NULL THEN project_taskitem.expected_time ELSE project_taskitem.actual_time END) FROM project_task, project_taskitem WHERE project_task.number = project_taskitem.task_num AND project_task.project_id = %s AND project_taskitem.is_current = %s AND project_taskitem.is_complete = %s  AND project_task.is_current = %s GROUP BY unit' % (self.id, True, True, True))
        data = cursor.fetchall()
        return data
    
    def start_month(self):
        cursor = connection.cursor()
        cursor.execute('SELECT monthname(expected_start_date), year(expected_start_date), count(id) FROM project_task WHERE project_id = %s AND is_current = %s GROUP BY month(expected_start_date), month(expected_start_date)' % (self.id, True))
        data = cursor.fetchall()
        return data
    
    def end_month(self):
        cursor = connection.cursor()
        cursor.execute('SELECT monthname(expected_end_date), year(expected_end_date), count(id) FROM project_task WHERE project_id = %s AND is_current = %s GROUP BY month(expected_end_date), month(expected_end_date)' % (self.id, True))
        data = cursor.fetchall()
        return data
    
    def user_tasks_sp(self, user):
        """How many tasks does a specific user have."""
        cursor = connection.cursor()
        stmt = "SELECT (CASE WHEN project_task.is_complete = 1 THEN 'Complete' Else 'In Progress' END) as status, count(project_task.id) FROM auth_user, project_task WHERE auth_user.id = project_task.user_responsible_id AND project_task.is_current = %s AND project_task.project_id = %s AND auth_user.id = %s GROUP BY project_task.is_complete ORDER BY status" % (True, self.id, user.id)
        print stmt
        cursor.execute(stmt)
        data = cursor.fetchall()
        return data
    
    def user_timeload(self):
        """How much load does a user have."""
        cursor = connection.cursor()
        stmt = 'SELECT auth_user.username, sum(CASE WHEN project_taskitem.actual_time IS NULL THEN project_taskitem.expected_time ELSE project_taskitem.actual_time END), unit FROM auth_user, project_taskitem, project_task WHERE project_taskitem.task_num = project_task.number AND project_taskitem.user_id = auth_user.id AND project_taskitem.is_current = %s  AND project_task.is_current = %s AND project_task.project_id = %s GROUP BY project_taskitem.user_id, project_taskitem.unit' % (True, True, self.id)
        print stmt
        cursor.execute(stmt)
        data = cursor.fetchall()
        return data
    
    def user_timeload_sp(self, user):
        """How much load does a specific user have."""
        cursor = connection.cursor()
        stmt = "SELECT (CASE WHEN project_taskitem.is_complete = 1 THEN 'Complete' Else 'In Progress' END) as status, sum(CASE WHEN project_taskitem.actual_time IS NULL THEN project_taskitem.expected_time ELSE project_taskitem.actual_time END), unit FROM auth_user, project_taskitem, project_task WHERE project_taskitem.task_num = project_task.number AND project_taskitem.user_id = auth_user.id AND project_taskitem.is_current = %s  AND project_task.is_current = %s AND project_task.project_id = %s AND auth_user.id = %s GROUP BY project_taskitem.is_complete, project_taskitem.unit ORDER BY status" % (True, True, self.id, user.id)
        print stmt
        cursor.execute(stmt)
        data = cursor.fetchall()
        return data
        
    def start_task_dates(self):
        """Number of tasks per day."""
        cursor = connection.cursor()
        cursor.execute('SELECT expected_start_date, count(expected_start_date) FROM project_task WHERE project_id = %s AND is_current = %s GROUP BY expected_start_date' % (self.id, True))
        data = cursor.fetchall()
        return data
        
    def task_start_dates_month(self, year, month):
        """Number of tasks per day."""
        cursor = connection.cursor()
        cursor.execute('SELECT expected_start_date, count(expected_start_date) FROM project_task WHERE project_id = %s AND is_current = %s AND year(expected_start_date) = %s AND month(expected_start_date) = %s GROUP BY expected_start_date' % (self.id, True, year, month))
        data = cursor.fetchall()
        return data
    
    def task_end_dates_month(self, year, month):
        """Number of tasks per day."""
        cursor = connection.cursor()
        cursor.execute('SELECT expected_end_date, count(expected_end_date) FROM project_task WHERE project_id = %s AND is_current = %s AND year(expected_end_date) = %s AND month(expected_end_date) = %s GROUP BY expected_end_date' % (self.id, True, year, month))
        data = cursor.fetchall()
        return data
    
    def get_task_hierachy(self):
        """REturn taks hiearchy as a nested list. This methods can be veru costly. Use carefully."""
        top_tasks = self.task_set.filter(parent_task_num__isnull = True)
        task_list = []
        for task in top_tasks:
            task_list.append(task)
            task_list.append(get_tree(task))
        return task_list
        
    class Admin:
        pass
    
options = (
        ('Owner', 'Owner'),
        ('Participant', 'Participant'),
        ('Viewer', 'Viewer'),
    )
    
class SubscribedUser(models.Model):
    """Users who have access to a given project
    user: the user
    project: the project
    group: access rights"""
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    group = models.CharField(max_length = 20, choices = options)
    
    def save(self):
        """Log it and save."""
        log_text = '%s has accepted invitation and is a %s of %s.' % (self.user.username, self.group, self.project.name)
        log = Log(project = self.project, text=log_text)
        log.save()
        super(SubscribedUser, self).save()
        
    def get_absolute_url(self):
        return '/%s/user/%s/' % (self.project.shortname, self.user.username)
        
    
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
    
    def save(self):
        """Log it and save."""
        log_text = '%s has been invited to as %s of %s.' % (self.user.username, self.group, self.project.name)
        log = Log(project = self.project, text=log_text)
        log.save()
        super(InvitedUser, self).save()    
    
    class Admin:
        pass    

class TaskManager(models.Manager):
    """Manager for model Task. It get only those rows which are current."""
    def get_query_set(self):
        """Modify the queryset returned by this, so we only get the curent tasks."""
        return super(TaskManager, self).get_query_set().filter(is_current = True)
    
    def all_include_old(self):
        """Get all the rows, including the versioned with old ones."""
        return super(TaskManager, self).all()
    
class SubtaskManager(models.Manager):
    """Manager for model Task. Used to get the subtasks for a task. Only gets the current subtasks."""
    def __init__(self, task, *args, **kwargs):
        super(SubtaskManager, self).__init__(*args, **kwargs)
        self.task = task
    def get_query_set(self):
        return Task.objects.filter(project = self.task.project, parent_task_num = self.task.number, is_current = True)
    
class ChildTaskItemManager(models.Manager):
    """Manager for model Task. Used to get the task items for a task. Only gets the current task items."""
    def __init__(self, task, *args, **kwargs):
        super(ChildTaskItemManager, self).__init__(*args, **kwargs)
        self.task = task
        
    def get_query_set(self):
        qs = TaskItem.objects.filter(project = self.task.project, task_num = self.task.number, is_current = True)
        return qs
    
class Task(models.Model):
    """Model for task.
    number: of the task under the current project.
    name: name for this task.
    project: the project under hwich this task was created.
    parent_task: For which task is this a subtask. If this is null, this is a task directly under project.
    user_responsible: who is the person who is responsible for completing this task.
    dates: excpected, and actual dates for this task.
    is_complete: has this task been completed? Defaults to false.
    
    created_on: when was this task created. Auto filled.
    is_delted: On deletion the task is not deleted, rather it is marked as deleted.
    created_by: The user who created this task.
    last_updated_by: The user who last updated this task item.
    
    effective_start_date: Since when is this version of the task in effect.
    effective_end_date: Till when was this version of the task in effect.
    version_number: What is the version number of the task. Starts at 1. Increments at each new version there after.
    is_current: Is this the current version of the task?
    
    objects: Modify to use a custom manager, so that we can get only the current task, and not the old versioned ones.
    all_objects: But have the old manager, when we want access to the old tasks as well, fo eg on history page.
    """
    
    number = models.IntegerField()
    name = models.CharField(max_length = 200)
    project = models.ForeignKey(Project)
    parent_task_num = models.IntegerField(null = True, blank = True)
    user_responsible = models.ForeignKey(User, null = True, blank = True)
    expected_start_date = models.DateField()
    expected_end_date = models.DateField(null = True, blank = True)
    actual_start_date = models.DateField(null = True,  blank = True)
    actual_end_date = models.DateField(null = True,  blank = True)
    is_complete = models.BooleanField(default = False)
    created_on = models.DateTimeField(auto_now_add = 1)
    is_deleted = models.BooleanField(default = False)
    created_by = models.ForeignKey(User, related_name = 'created_tasks')
    last_updated_by = models.ForeignKey(User, related_name = 'updated_tasks')
    #Versioning
    effective_start_date = models.DateTimeField(auto_now_add = True)
    effective_end_date = models.DateTimeField(null = True, auto_now = True)
    version_number = models.IntegerField()
    is_current = models.BooleanField(default = True)
    
    objects = TaskManager()
    all_objects = models.Manager()
    
    def __unicode__(self):
        return self.name
    
    def __str__(self):
        return self.name
    
    @classmethod
    def as_csv_header(self):
        return ('Name', 'User', 'Start Date', 'End Date', 'Actual Start Date', 'Actual End Date', 'Is Complete')
    
    def as_csv(self):
        return (self.name, self.user_responsible, self.expected_start_date, self.expected_end_date, self.actual_start_date, self.actual_end_date, self.is_complete)
    
    def get_sub_tasks(self):
        """Get subtasks for this task."""
        return Task.objects.filter(project = self.project, parent_task_num = self.number)
    
    def __init__(self, *args, **kwargs):
        """Update the details managers to show only the current objects, and drop old versioned ones."""
        super(Task, self).__init__(*args, **kwargs)
        self.task_set = SubtaskManager(self)
        self.taskitem_set = ChildTaskItemManager(self)
    
    def save(self):
        """If this is the firsts time populate required details, if this is update version it."""
        if not self.id:
            self.version_number = 1
            cursor = connection.cursor()
            cursor.execute('SELECT MAX(number) from project_task WHERE project_id = %s' % self.project.id)
            num = cursor.fetchone()[0]
            if not num:
                num = 0
            self.number = num + 1#Task.objects.filter(project = self.project, is_current = True).count() + 1
            if self.user_responsible:
                log_text = 'Task %s has for %s been created.  ' % (self.name, self.user_responsible)
            else:
                log_text = 'Task %s has been created.  ' % self.name
            log_description = 'Task was created by %s on %s' % (self.created_by.username, time.strftime('%d %B %y'))
            log = Log(project = self.project, text=log_text, description = log_description)
            log.save()             
            super(Task, self).save()
        else:
            #Version it
            import copy
            new_task = copy.copy(self)
            """self.is_current = False
            self.effective_end_date = datetime.datetime.now()
            super(Task, self).save()"""
            self.update_field('is_current', False)
            new_task.id = None
            new_task.is_current = True
            new_task.version_number = self.version_number + 1
            if self.user_responsible:
                log_text = 'Task %s for %s has been updated.  ' % (self.name, self.user_responsible)
            else:
                log_text = 'Task %s has been updated' % (self.name)
            log_description = 'Task was updated by %s on %s' % (self.last_updated_by.username, time.strftime('%d %B %y'))
            log = Log(project = self.project, text=log_text, description = log_description)
            log.save()            
            super(Task, new_task).save()
            
    def save_without_versioning(self):
        """Have a way to Save without versioning, as we overriden save()"""
        super(Task, self).save()
        
    def update_field(self, field, value):
        """Update a field without updating any other field. We need this when we are versioning a Task and we want to save
        the objects to set its is_current, but not modify any other field."""
        cursor = connection.cursor()
        stmt = 'UPDATE project_task SET %s = %s WHERE id = %s' % (field, value, self.id)
        print stmt
        cursor.execute(stmt)
        
        
    def as_text(self):
        """Return a summary textual representation of the task."""
        txt = 'Name: %s \n Start Date: %s \n End Date: %s \n Person responsible: %s \n Is Complete?: %s \n Actual start date: %s \n Actual end date: %s' % (self.name, self.expected_start_date, self.expected_end_date, self.user_responsible, self.is_complete, self.actual_start_date, self.actual_end_date)
        return txt
        
    def set_is_complete(self, value):
        """If a task is marked as complete all its sub tasks and task items should be marked as complete."""
        self.is_complete = value
        if value:
            cursor = connection.cursor()
            cursor.execute('UPDATE project_task SET is_complete = %s WHERE parent_task_num = %s' % (True , self.number))
            cursor.execute('UPDATE project_taskitem SET is_complete = %s WHERE task_num = %s' % (True, self.number))
    
    def get_is_complete(self):
        return self.is_complete
    
    """Expose this as a property."""
    is_complete_prop = property(get_is_complete, set_is_complete)            
            
    def get_old_versions(self):
        """Get all the versions of this task."""
        return Task.all_objects.filter(number = self.number, project  = self.project).order_by('-created_on')
            
    def num_child_tasks(self):
        """Get number of subtasks for this task."""
        return self.task_set.all().count()
    
    def num_items(self):
        """Get number of taskitems for this task."""
        return self.taskitem_set.all().count()
    
    def get_absolute_url(self):
        """Get url to details for this task."""
        return '/%s/taskdetails/%s/' % (self.project.shortname, self.number)
    
    def version_url(self):
        """Get url to old versions for this task."""
        return '/%s/taskhistory/%s/' % (self.project.shortname, self.number)
    
    def revision_url(self):
        """Get url to details for this task."""
        return '/%s/taskrevision/%s/' % (self.project.shortname, self.id)
    
    def edit_url(self):
        """Get url to editing for this task."""
        return '/%s/edittask/%s/' % (self.project.shortname, self.number)
    
    def add_note_url(self):
        return '/%s/taskdetails/%s/addnote/' % (self.project.shortname, self.number)
    
    def add_note(self, text, user):
        """Add a note to this task."""
        note = TaskNote(text = text, user = user)
        note.task_num = self.number
        note.save()
        return note
    
    def get_notes(self):
        """Get notes for this task."""
        return TaskNote.objects.filter(task_num = self.number)
    
    class Meta:
        ordering = ('-created_on',)
            
    class Admin:
        pass                  


class TaskItemManager(models.Manager):
    def get_query_set(self):
        return super(TaskItemManager, self).get_query_set().filter(is_current = True) 
unit_choices = (
    ('Hours', 'Hours'),
    ('Days', 'Days'),
    ('Months', 'Months'),
    )    
class TaskItem(models.Model):
    """A task item for a task.
    number: Number of the taskitem. This remains same across versions, (But the ids change).
    project: Project which this task item is created for.
    task_num: number of the task for which this is a taskitem.
    name: name of the taskitem.
    user: user who needs to do this taskitem.
    expected time: How much time this todo should take.
    actual_time: How much time this todo actually took.
    unit: the unit in which you want to measure the time. Can be hours, days or months.
    is_complete: Has this todo item been completed.
    
    created_on: When was this todo created. AUto filled.
    created_by: Who was the user who created this task.
    last_updated_by: Who was the user who last updated this taskitem.
    is_delted: When a taskitem is marked as deleted, it is not acually deleted but rather the flag is set, to mark its delted status.
    
    effective_start_date: Since when is this version of the task in effect.
    effective_end_date: Till when was this version of the task in effect.
    version_number: What is the version number of the task. Starts at 1. Increments at each new version there after.
    is_current: Is this the current version of the task?
    
    objects: Modify to use a custom manager, so that we can get only the current taskitem, and not the old versioned ones.
    all_objects: But have the old manager, when we want access to the old taskitems as well, for eg on history page.
    """
    number = models.IntegerField()
    project = models.ForeignKey(Project)
    task_num = models.IntegerField()
    name = models.CharField(max_length = 200)
    user = models.ForeignKey(User, null = True)
    expected_time = models.DecimalField(decimal_places = 2, max_digits = 10)
    actual_time = models.DecimalField(decimal_places = 2, max_digits = 10, null = True)
    unit = models.CharField(max_length = 20, choices = unit_choices)
    is_complete = models.BooleanField(default = False)
    
    created_on = models.DateTimeField(auto_now_add = 1)
    created_by = models.ForeignKey(User, related_name = 'created_taskitems')
    last_updated_by = models.ForeignKey(User,  related_name = 'updated_taskitems')
    is_deleted = models.BooleanField(default = False)
    #Versioning
    effective_start_date = models.DateTimeField(auto_now_add = 1)
    effective_end_date = models.DateTimeField(null = True)
    version_number = models.IntegerField()
    is_current = models.BooleanField(default = True)
    
    objects = TaskItemManager()
    all_objects = models.Manager()
    
    def save(self):
        """If this is the firsts time populate required details, if this is update version it."""
        if not self.id:
            self.version_number = 1
            self.number = -1
            cursor = connection.cursor()
            cursor.execute('SELECT MAX(number) from project_taskitem WHERE project_id = %s' % self.project.id)
            num = cursor.fetchone()[0]
            if not num:
                num = 0
            self.number = num + 1
            super(TaskItem, self).save()
            log_text = 'Item %s created for task %s.' % (self.name, self.task.name)
            log_description = 'Item was created by %s on %s' % (self.created_by.username, time.strftime('%d %B %y'))
            log = Log(project = self.task.project, text = log_text, description = log_description)
            log.save()
        else:
            #Version it
            import copy
            new_item = copy.copy(self)
            self.is_current = False
            self.effective_end_date = datetime.datetime.now()
            super(TaskItem, self).save()
            cursor = connection.cursor()
            foo = 'SELECT MAX(version_number) from project_taskitem WHERE project_id = %s AND number = %s' % (self.project.id, self.number)
            print foo
            cursor.execute(foo)
            num = cursor.fetchone()[0]
            if not num:
                num = 0
            new_item.version_number = num + 1
            new_item.is_current = True
            new_item.id = None
            super(TaskItem, new_item).save()
            print new_item.version_number
            log_text = 'Item %s for taks %s has been updated.' % (self.name, self.task.name)
            log_description = 'Task was updated by %s on %s' % (self.last_updated_by.username, time.strftime('%d %B %y'))
            log = Log(project = self.task.project, text = log_text, description = log_description)
            log.save()
            
    def save_without_versioning(self):
        """But we migth want the old save which we have overriden. So provide a method which does not version."""
        super(TaskItem, self).save()
        
    def as_text(self):
        """Summary representation of the taskitem."""
        txt = 'Name: %s \n Task: %s \n Expected time: %s %s \n Actual time: %s %s User: %s' % (self.name, self.task.name, self.expected_time, self.unit, self.actual_time, self.unit, self.user)
        return txt
    
    @classmethod
    def as_csv_header(self):
        return ('Name', 'Time', 'User', 'Complete?')
    
    def as_csv(self):
        return (self.name, str(self.expected_time) + self.unit, self.user, self.is_complete)
    
            
    def get_task(self):
        """Get the task from the taskitem. This is not a direct FK reference as the tasks may be versioned."""
        return Task.objects.get(project = self.project, number = self.task_num, is_current = True)
    task = property(get_task, None, None)
    
    def version_url(self):
        """The url to see old versions for the taskitem."""
        return '/%s/taskitemhist/%s/' % (self.project, self.number)
            
    def edit_url(self):
        """The url to edit the taskitem."""
        return '/%s/edititem/%s/' % (self.project, self.number)
    
    def revision_url(self):
        """The url where a previous revision can be seen."""
        return '/%s/itemrevision/%s/' % (self.task.project, self.id)
        
    
    def old_versions(self):
        """return all versions of the taskitem."""
        return TaskItem.all_objects.filter(project = self.project, number = self.number).order_by('-version_number')
    
    
    
    def time_worked(self):
        """Get the time worked."""
        if self.actual_time:
            time = self.actual_time
        else:
            time = self.expected_time
        return '%s %s' % (time, self.unit)
            
    class Admin:
        pass
    
class TodoList(models.Model):
    """A todo list of a user of the project.
    name: name of the todo list.
    user: User for which this todo list is created.
    project: Project under which this list is created.
    is_complete_attr: Is this list complete?
    created_on: When was this list created?
    """
    name = models.CharField(max_length = 200)
    user = models.ForeignKey(User)
    project = models.ForeignKey(Project)
    is_complete_attr = models.BooleanField(default = False)
    created_on = models.DateTimeField(auto_now_add = 1)
    
    def get_is_complete(self):
        """Get if list is complete."""
        return self.is_complete_attr
    
    @classmethod
    def as_csv_header(self):
        return ('List Name', 'Is Complete?')
    
    def as_csv(self):
        return (self.name, self.is_complete)
        
    
    def set_is_complete(self, is_complete_attr):
        """Get if list is complete.
        When it is, mark all todo items as done too."""
        print 'asdf'
        self.is_complete_attr = is_complete_attr
        self.save()
        cursor = connection.cursor()
        cursor.execute('UPDATE project_todoitem SET is_complete = %s WHERE list_id = %s', (True, self.id))
    
    """Expose the previous two method as a property."""    
    is_complete = property(get_is_complete, set_is_complete, None)
    
    def get_item_form(self):
        """Get the form to add an item."""
        return AddTodoItemForm(self)
    
    """And expose it as a property."""
    item_form = property(get_item_form, None, None)
    
    class Admin:
        pass
    
class TodoItem(models.Model):
    """A todo item of the project."""
    list = models.ForeignKey(TodoList)
    text = models.CharField(max_length = 200)
    is_complete = models.BooleanField(default = False)
    created_on = models.DateTimeField(auto_now_add = 1)
    
    @classmethod
    def as_csv_header(self):
        return ('List Name', 'Todo Item', 'Is Complete?')
    
    def as_csv(self):
        return (self.list.name, self.text, self.is_complete)
    
    class Admin:
        pass
    
class Log(models.Model):
    """Log of the project.
    project: Project for which this log is written.
    text: Text of the log.
    created_on: When was this log created."""
    project = models.ForeignKey(Project)
    text = models.CharField(max_length = 200)
    description = models.CharField(max_length = 200, null = True)
    created_on = models.DateTimeField(auto_now_add = 1)
    
    def get_absolute_url(self):
        return '/%s/logs/' % self.project.shortname
    
    def __unicode__(self):
        return '%s (Logged on %s)' % (self.text, self.created_on)
    
    @classmethod
    def as_csv_header(self):
        return ('Log Text', 'Description', 'Logged on')
    
    def as_csv(self):
        return (self.text, self.description, self.created_on.strftime('%Y-%m-%d'))
    
    class Meta:
        ordering = ('-created_on', )
    
    class Admin:
        pass
    
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
    
    @classmethod
    def as_csv_header(self):
        return ('Notice Text', 'Notice created by', 'Created on')
    
    def as_csv(self):
        return (self.text, self.user.username, self.created_on.strftime('%Y-%m-%d'))    
    
    class Admin:
        pass
    
    class Meta:
        ordering = ('-created_on',)
    
class WikiPage(models.Model):
    """Model of the wiki page.
    name: name of the page, should be alphanumeric. Shown in url.
    Title: title for the page. Can contain spaces.
    current_revion: the wiki_page which is the current revision for this page.
    created_on: When was this page created. Auto filled.
    is_deleted: Set this flat when the page needs to be delted.
    """
    name = models.CharField(max_length = 20)
    title = models.CharField(max_length = 200)
    project = models.ForeignKey(Project)
    current_revision = models.ForeignKey('WikiPageRevision', null = True)
    created_on = models.DateTimeField(auto_now_add = 1)
    is_deleted = models.BooleanField(default = True)
    
    def edit_url(self):
        return '/%s/wiki/%s/edit/' % (self.project.shortname, self.name)
    
    def get_absolute_url(self):
        return '/%s/wiki/%s/' % (self.project.shortname, self.name)
    
    def version_url(self):
        return '/%s/wiki/%s/revisions/' % (self.project.shortname, self.name)
    
    def save(self):
        if not self.name:
            name = '_'.join(self.title.split())
            count = WikiPage.objects.filter(name__istartswith=name).count()
            if count:
                name = '%s_%s' % (name, count)
            name = name[:19]
            self.name = name
        log_text = 'Wiki page %s has been created.' % self.title
        log_description = None#'Page was created by %s on %s' % (self.current_revision.user.username, time.strftime('%d %B %y'))
        log = Log(project = self.project, text = log_text, description = log_description)
        log.save()
        super(WikiPage, self).save()
        
    
    
    def delete(self):
        """Wiki pages can not be deleted. If a delete request comes, the is_deleted flag is set to true."""
        is_deleted = True
        self.save()
        
    class Admin:
        pass
    
class WikiPageRevision(models.Model):
    """user: The user who wrote this page revision.
    wiki_page: The page for which this revision is created.
    wiki_text: The text entered for this revion.
    html_text: The text converted to html.
    created_on: When was this revision created. Auto filled.
    
    Version_number: Version number for this revision. Starts from 1 and increemnst there after.
    """
    user = models.ForeignKey(User)
    wiki_page = models.ForeignKey(WikiPage)
    wiki_text = models.TextField()
    html_text = models.TextField()
    created_on = models.DateTimeField(auto_now_add = 1)
    version_number = models.IntegerField(default = 0)
    
    def save(self):
        self.html_text = self.wiki_text
        log_text = 'A revision for wiki page %s has been created.' % self.wiki_page.title
        log_description = 'Revision was created by %s on %s.' % (self.user.username, time.strftime('%d %B %y'))
        log = Log(project = self.wiki_page.project, text = log_text, description = log_description)
        last_version = WikiPageRevision.objects.filter(wiki_page = self.wiki_page).count()
        self.version_number = last_version + 1
        log.save()
        super(WikiPageRevision, self).save()
        
    def get_absolute_url(self):
        return '/%s/wiki/%s/revisions/%s/' % (self.wiki_page.project.shortname, self.wiki_page.name, self.id)
        
    class Admin:
        pass
    
    class Meta:
        ordering = ('-created_on',)
    
    
class TaskNote(models.Model):
    """
    Task_num: The task for which this note is created.
    We cant just use a foreign key coz, the note is for a specific task number, not a revision of it.
    text: Text of the noe.
    user: User who wrote this note.
    created_on: When wa sthis note created.
    """
    task_num = models.IntegerField()
    text = models.TextField()
    user = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now_add = 1)  
    
    
class ProjectFile(models.Model):
    """project: The project for which this file is attached.
    filename: name of the file.
    """
    project = models.ForeignKey(Project)
    filename = models.CharField(max_length = 200)
    #user = models.ForeignKey(User)
    created_on = models.DateTimeField(auto_now_add = 1)
    current_revision = models.ForeignKey('ProjectFileVersion', related_name = 'this_file', null = True)
    total_size = models.IntegerField()
    
    def size_str(self):
        "String representation of size"
        size = self.total_size
        if not (size / (1000 * 1000 )) == 0:
            size = float(size)/(1000 * 1000)
            return '%s %s'% (size, 'MB')
        elif not (size / (1000)) == 0:
            size = float(size)/(1000 )
            return '%s %s'% (size, 'KB')
        else:
            return '%s %s'% (size, 'bytes')
        
    def save(self):
        "Save and log."
        log = Log(text = "File %s has been added to %s." % (self.filename, self.project.name), project = self.project)
        log.description = 'File was created on %s' % time.strftime('%d %B %y')
        log.save()
        super(ProjectFile, self).save()
    
    def __unicode__(self):
        return u'%s' % self.filename
    
    class Meta:
        ordering = ('-created_on', )
    
    class Admin:
        pass
    
class ProjectFileVersion(models.Model):
    """A specific version of the file uploaded.
    file: file for which this revision was created.
    revision_name: Name under which this revision is saved.
    version_number = version number of the file uploaded. Starts at 1. Increments thereafter.
    user: The user who created this file.
    size: size of this file revision.
    """
    file = models.ForeignKey(ProjectFile)
    revision_name = models.CharField(max_length = 200)
    version_number = models.IntegerField()
    user = models.ForeignKey(User)
    size = models.IntegerField()
    created_on = models.DateTimeField(auto_now_add = 1)
    
    def save(self):
        "Save and log."
        log = Log(text = "New revision for file %s has been created." % (self.filename, self.project.name), project = self.file.project)
        log.description = 'Revision was created on %s' % time.strftime('%d %B %y')
        log.save()
        super(ProjectFileVersion, self).save()
    
    def get_name(self):
        #return '%s-%s' % (self.file.filename,self.version_number)
        return self.revision_name
    
    def get_s3_url(self):
        import secrets
        import S3
        import defaults
        gen = S3.QueryStringAuthGenerator(secrets.aws_id, secrets.aws_key)
        #url = gen.get(defaults.bucket, '/%s/%s' % (self.file.project.shortname, self.get_name()))
        url = gen.get(defaults.bucket, '%s' % (self.get_name()))
        return url
        
    def save(self):
        last_version = self.file.projectfileversion_set.count()
        self.version_number = last_version + 1
        super(ProjectFileVersion, self).save()
    
    class Admin:
        pass
    
    class Meta:
        ordering = ('-version_number', )

def get_tree(task):
    "Given a task return its sub task hiearchy"
    task_list = []
    subt = task.task_set.all()
    for task in subt:
        print task
        task_list.append(task)
        children = get_tree(task)
        if children:
            task_list.append(children)
    return task_list
    


    
    

