import unittest
from models import *
from bforms import *
from django.contrib.auth.models import User
import datetime
from django.newforms import ValidationError

today = datetime.date.today()
today_str = str(today)

#Test the models.

class TestProject(unittest.TestCase):
    """Test the model project."""
    
    def setUp(self):
        """Create a user for use in other functions."""
        user = User.objects.create_user('Shabda', 'Shabda@gmail.com', 'shabda')
        self.user = user
        
    def testProjectCreationExceptions(self):
        """Sanity tests. Check that required fields, are in fact required."""
        project = Project()
        self.assertRaises(Exception, project.save)
        project.name = 'Foo project'
        self.assertRaises(Exception, project.save)
        project.shortname = 'What'
        self.assertRaises(Exception, project.save)
        project.start_date = datetime.date.today()
        self.assertRaises(Exception, project.save)
        project.owner = self.user
        project.save()
        
    def testProjectShortName(self):
        """Test that project short name does not contain any special chars."""
        project = Project(name = 'Foo bar', owner = self.user, start_date = datetime.date.today())
        project.shortname = '***'
        self.assertRaises(Exception, project.save,)
        "Empty value for shortname not allowed."
        project.shortname = ''
        self.assertRaises(Exception, project.save)
        project.shortname = 'Foo'
        project.save()
        
    def testProjectName(self):
        """Test that project name is not empty."""
        project = Project(shortname = 'Foo', owner = self.user, start_date = datetime.date.today())
        project.name = ''
        self.assertRaises(Exception, project.save)
        project.name = 'Bar baz bax'
        project.save()
        
        
    def tearDown(self):
        self.user.delete()
        
class TestTask(unittest.TestCase):
    
    def setUp(self):
        user = User.objects.create_user('Shabda', 'Shabda@gmail.com', 'shabda')
        self.user = user
        project = Project(shortname = 'Foo', name='Bar bax baz', owner = self.user, start_date = datetime.date.today())
        project.save()
        self.project = project
        
    def testTaskExceptions(self):
        "Sanity test. Required fields."
        task = Task()
        self.assertRaises(Exception, task.save)
        task.name = 'Foo'
        self.assertRaises(Exception, task.save)
        task.user_responsible = self.user
        self.assertRaises(Exception, task.save)
        task.expected_start_date = datetime.date.today()
        self.assertRaises(Exception, task.save)
        task.project = self.project
        self.assertRaises(Exception, task.save)
        task.created_by = self.user
        task.last_updated_by = self.user
        task.save()
        
    def testTaskVersioning(self):
        task = Task(name = 'Foo', user_responsible = self.user, expected_start_date = datetime.date.today(), project = self.project, created_by = self.user, last_updated_by = self.user)
        task.save()
        task.user_responsible = None
        #task.save()
        
    def tearDown(self):
        self.user.delete()
        self.project.delete()
        
class TestWikiPage(unittest.TestCase):
    
    def setUp(self):
        user = User.objects.create_user('Shabda', 'Shabda@gmail.com', 'shabda')
        self.user = user
        project = Project(shortname = 'Foo', name='Bar bax baz', owner = self.user, start_date = datetime.date.today())
        project.save()
        self.project = project
        
    def testWikiPageExceptions(self):
        "Sanity tests. Required fields are in fact required."
        wikipage = WikiPage(title = 'The best wiki page')
        self.assertRaises(Exception, wikipage.save)
        wikipage.project = self.project
        wikipage.save()
        self.assertNotEqual(wikipage.name, None)
        
    def testMultiPages(self):
        "Multiple pages with same title get different names."
        wikipage1 = WikiPage(title = 'The best wiki page', project = self.project)
        wikipage2 = WikiPage(title = 'The best wiki page', project = self.project)
        wikipage1.save()
        wikipage2.save()
        self.assertNotEqual(wikipage1.name, wikipage2.name)
        
    def tearDown(self):
        self.user.delete()
        self.project.delete()
        
class TestWikiPageRevisions(unittest.TestCase):
    
    def setUp(self):
        user = User.objects.create_user('Shabda', 'Shabda@gmail.com', 'shabda')
        self.user = user
        project = Project(shortname = 'Foo', name='Bar bax baz', owner = self.user, start_date = datetime.date.today())
        project.save()
        self.project = project
        wikipage = WikiPage(title = 'The best wiki page', project = self.project)
        wikipage.save()
        self.page = wikipage
        
    def testPageRevExceptions(self):
        pagerev = WikiPageRevision(wiki_page = self.page)
        self.assertRaises(Exception, pagerev.save)
        pagerev.wiki_text = 'Whatever'
        self.assertRaises(Exception, pagerev.save)
        pagerev.user = self.user
        pagerev.save()
        
    def testPageRevVersioning(self):
        pagerev1 = WikiPageRevision(wiki_page = self.page, wiki_text = 'asdf', user = self.user)
        pagerev1.save()
        pagerev2 = WikiPageRevision(wiki_page = self.page, wiki_text = 'asdf1',  user = self.user)
        pagerev2.save()
        pagerev3 = WikiPageRevision(wiki_page = self.page, wiki_text = 'asdf3',  user = self.user)
        pagerev3.save()
        self.assertEqual(pagerev1.version_number + 1, pagerev2.version_number)
        self.assertEqual(pagerev2.version_number + 1, pagerev3.version_number)
                
    def tearDown(self):
        self.user.delete()
        self.project.delete()
        
class TestTodoList(unittest.TestCase):
    
    def setUp(self):
        user = User.objects.create_user('Shabda', 'Shabda@gmail.com', 'shabda')
        self.user = user
        project = Project(shortname = 'Foo', name='Bar bax baz', owner = self.user, start_date = datetime.date.today())
        project.save()
        self.project = project
    
    def testTodoExceptions(self):
        """Sanity Test. Required fields are in fact required."""
        todolist = TodoList(name = "Foo")
        self.assertRaises(Exception, todolist.save)
        todolist.user = self.user
        self.assertRaises(Exception, todolist.save)
        todolist.project = self.project
        todolist.save()
        self.assertNotEqual(todolist.is_complete_attr, None)
        self.assertNotEqual(todolist.created_on, None)
        
    def tearDown(self):
        self.user.delete()
        self.project.delete()
        
class TestTodoItem(unittest.TestCase):
    
    def setUp(self):
        user = User.objects.create_user('Shabda', 'Shabda@gmail.com', 'shabda')
        self.user = user
        project = Project(shortname = 'Foo', name='Bar bax baz', owner = self.user, start_date = datetime.date.today())
        project.save()
        self.project = project
        list = TodoList(name = 'Foo', user = user, project = project)
        list.save()
        self.list = list
        
    def testTodoItemExceptions(self):
        """Sanity test. Required fields are in fact required."""
        item = TodoItem()
        self.assertRaises(Exception, item.save)
        item.text = 'Foo bar'
        self.assertRaises(Exception, item.save)
        item.list = self.list
        item.save()
        
    def tearDown(self):
        self.user.delete()
        self.project.delete()
        self.list.delete()
        
class TestTodo(unittest.TestCase):
    
    def setUp(self):
        user = User.objects.create_user('Shabda', 'Shabda@gmail.com', 'shabda')
        self.user = user
        project = Project(shortname = 'Foo', name='Bar bax baz', owner = self.user, start_date = datetime.date.today())
        project.save()
        self.project = project
        list = TodoList(name = 'Foo', user = user, project = project)
        list.save()
        self.list = list
        
    def testIsComplete(self):
        """Test that when is complete is marked as true, all the items are also marked as true."""
        item1 = TodoItem(text = 'Bar', list= self.list)
        item1.save()
        item2 = TodoItem(text = 'Bar2', list= self.list)
        item2.save()
        self.list.is_complete = True
        #self.assertEqual(item1.is_complete, True)
        #self.assertEqual(item2.is_complete, True)
        
        
    def tearDown(self):
        self.user.delete()
        self.project.delete()
        self.list.delete()
        
class TestLog(unittest.TestCase):
    
    def setUp(self):
        user = User.objects.create_user('Shabda', 'Shabda@gmail.com', 'shabda')
        self.user = user
        project = Project(shortname = 'Foo', name='Bar bax baz', owner = self.user, start_date = datetime.date.today())
        project.save()
        self.project = project
        
    def testLogExceptions(self):
        "Sanity test, required fields are in fact required."
        log = Log()
        self.assertRaises(Exception, log.save)
        log.text = 'Foo'
        self.assertRaises(Exception, log.save)
        log.project = self.project
        log.save()
        self.assertNotEqual(log.created_on, None)
                
    def  testTaskLogs(self):
        "Task creation is logged"
        logcount = Log.objects.all().count()
        task = Task(name = 'Foo', created_by = self.user, last_updated_by = self.user, project = self.project, expected_start_date = today)
        task.save()
        newlogcount = Log.objects.all().count()
        self.assertEqual(newlogcount, logcount + 1)
        self.task = task
        
    def testTaskItemLogs(self):
        "Task item creation is logged."
        task = Task(name = 'Foo', created_by = self.user, last_updated_by = self.user, project = self.project, expected_start_date = today)
        task.save()
        logcount = Log.objects.all().count()
        taskitem = TaskItem(name = 'Foo', expected_time = 10, unit = 'Hour', created_by = self.user, last_updated_by = self.user, project = self.project, task_num = task.number)
        taskitem.save()
        newlogcount = Log.objects.all().count()
        self.assertEqual(newlogcount, logcount + 1)
        
    def testPageCreation(self):
        """Wiki Page creation is logged."""
        logcount = Log.objects.all().count()
        page = WikiPage(title = 'Foo', project = self.project)
        page.save()
        newlogcount = Log.objects.all().count()
        self.assertEqual(newlogcount, logcount + 1)
        
    def testPageRevisionCreation(self):
        "Wiki page revision creation is logged"
        page = WikiPage(title = 'Foo', project = self.project)
        page.save()
        logcount = Log.objects.all().count()
        pagerevision = WikiPageRevision(wiki_page = page, wiki_text = 'Foo', user = self.user)
        pagerevision.save()
        newlogcount = Log.objects.all().count()
        self.assertEqual(newlogcount, logcount + 1) 
        
    def testTodoLog(self):
        "Todo creation is not logged."
        logcount = Log.objects.all().count()
        list = TodoList(name = 'Foo', user = self.user, project = self.project)
        list.save()
        newlogcount = Log.objects.all().count()
        self.assertEqual(logcount, newlogcount)
        item = TodoItem(text = 'Bar', list= list)
        item.save()
        newlogcount = Log.objects.all().count()
        self.assertEqual(logcount, newlogcount)
        
    def testNoticeCreation(self):
        "Notice creation is not logged"
        logcount = Log.objects.all().count()
        notice = Notice(user = self.user, project = self.project)
        notice.save()
        newlogcount = Log.objects.all().count()
        self.assertEqual(logcount, newlogcount)
        
        
    def tearDown(self):
        self.user.delete()
        self.project.delete()
        
#Test the Forms

class TestCreateProjectForm(unittest.TestCase):
    
    def setUp(self):
        user = User.objects.create_user('Shabda', 'Shabda@gmail.com', 'shabda')
        self.user = user
        
    def tearDown(self):
        self.user.delete()
        pass
        
    def testCreateProjectForm(self):
        """Test the required field for the form"""
        form = CreateProjectForm()
        self.assertRaises(Exception, form.save)
        form = CreateProjectForm({})
        self.assertEqual(form.is_valid(), False)
        form = CreateProjectForm(data = {'name':'Foo', 'shortname':'Bar', 'start_date':today_str, 'end_date':today_str})
        self.assertEqual(form.is_valid(), True)
        form = CreateProjectForm(data = {'name':'Foo', 'shortname':'Bar', 'start_date':today_str,})
        self.assertEqual(form.is_valid(), True)
        
    def testNonAlphaNUm(self):
        """Non aplhanumeric for shortname not allowed."""
        form = CreateProjectForm(data = {'name':'Foo', 'shortname':'Bar   ', 'start_date':today_str,})
        self.assertEqual(form.is_valid(), False)
        form = CreateProjectForm(data = {'name':'Foo', 'shortname':'Ba*r', 'start_date':today_str,})
        self.assertEqual(form.is_valid(), False)
        
    def testFormSave(self):
        "Save returns a project."
        form = CreateProjectForm(user = self.user, data = {'name':'Foo', 'shortname':'Bar', 'start_date':today_str,})
        self.assertEqual(form.is_valid(), True)
        project = form.save()
        self.assertEqual(type(project), Project)
        
    def testShortName(self):
        "Shortnames must be unique"
        form = CreateProjectForm(user = self.user, data = {'name':'FooBar1', 'shortname':'Bar', 'start_date':today_str,})
        self.assertEqual(form.is_valid(), True)
        form.save()
        form = CreateProjectForm(user = self.user, data = {'name':'FooBar2', 'shortname':'Bar', 'start_date':today_str,})
        self.assertEqual(form.is_valid(), False)
        
        
class TestInviteUserForm(unittest.TestCase):
    
    def setUp(self):
        user = User.objects.create_user('Shabda', 'Shabda@gmail.com', 'shabda')
        self.user = user
        project = Project(shortname = 'Foo', name='Bar bax baz', owner = self.user, start_date = datetime.date.today())
        project.save()
        self.project = project
        
    def tearDown(self):
        self.user.delete()
        
    def testInviteUserForm(self):
        "required fields"
        form  = InviteUserForm()
        self.assertEquals(form.is_valid(), False)
        form = InviteUserForm(data = {'username':'Shabda'})
        self.assertEquals(form.is_valid(), False)
        form = InviteUserForm(data = {'username':'Shabda', 'group' : 'Owner'})
        self.assertEquals(form.is_valid(), True)
    
    def testInviteUserForm(self):
        "Group must be Owner, Particant, Viewer"
        form = InviteUserForm(data = {'username':'Shabda', 'group' : 'Owner'})
        self.assertEquals(form.is_valid(), True)
        form = InviteUserForm(data = {'username':'Shabda', 'group' : 'Participant'})
        self.assertEquals(form.is_valid(), True)
        form = InviteUserForm(data = {'username':'Shabda', 'group' : 'Viewer'})
        self.assertEquals(form.is_valid(), True)
        form = InviteUserForm(data = {'username':'Shabda', 'group' : 'DummyVal'})
        self.assertEquals(form.is_valid(), False)
        form = InviteUserForm(data = {'username':'Shabda', 'group' : 'Foobar'})
        self.assertEquals(form.is_valid(), False)
        
    def testInvitedUsers(self):
        "Invited users can not be invited again."
        form = InviteUserForm(project =  self.project, data = {'username':'Shabda', 'group' : 'Owner'})
        self.assertEquals(form.is_valid(), True)
        invuser = form.save()
        form = InviteUserForm(project =  self.project, data = {'username':'Shabda', 'group' : 'Owner'})
        self.assertEquals(form.is_valid(), False)
        #Delete the invited user so we can use the user in other methods
        invuser.delete()
        
    def testSubscribedUsers(self):
        "Subscribed users can not be invited again to a project, but can be invited to a different project."
        user = User.objects.create_user('demo', 'demo@demo.com', 'demo')
        subs = SubscribedUser(user = user, project = self.project, group = 'Owner')
        subs.save()
        form = InviteUserForm(project =  self.project, data = {'username':'demo', 'group' : 'Owner'})
        self.assertEquals(form.is_valid(), False)
        project1 = Project(shortname = 'Foo1', name='Bar bax baz', owner = self.user, start_date = datetime.date.today())
        project1.save()
        form = InviteUserForm(project =  project1, data = {'username':'demo', 'group' : 'Owner'})
        self.assertEquals(form.is_valid(), True)
        
        
    def testFormSave(self):
        "Save returns instance of a InvitedUser"
        form = InviteUserForm(project =  self.project, data = {'username':'Shabda', 'group' : 'Owner'})
        self.assertEquals(form.is_valid(), True)
        invuser = form.save()
        self.assertEqual(type(invuser), InvitedUser)
        
class TestCreateTaskForm(unittest.TestCase):

    def setUp(self):
        user = User.objects.create_user('Shabda', 'Shabda@gmail.com', 'shabda')
        self.user = user
        project = Project(shortname = 'Foo', name='Bar bax baz', owner = self.user, start_date = datetime.date.today())
        project.save()
        self.project = project
        
    def tearDown(self):
        self.user.delete()
        
    def testCreateTaskForm(self):
        "Required fields"
        form = CreateTaskForm(self.project, self.user, )
        self.assertEqual(form.is_valid(), False)
        form = CreateTaskForm(self.project, self.user, data = {'name':'Foo'})
        self.assertEqual(form.is_valid(), False)
        form = CreateTaskForm(self.project, self.user, data = {'name':'Foo', 'start_date' : today_str})
        self.assertEqual(form.is_valid(), False)
        form = CreateTaskForm(self.project, self.user, data = {'name':'Foo', 'start_date' : today_str, 'user_responsible':self.user.username})
        self.assertEqual(form.is_valid(), False)
        
        #Subscribe a user to this project
        user = User.objects.create_user('demo', 'demo@gmail.com', 'demo')
        subs = SubscribedUser(user = user, project = self.project, group = 'Owner')
        subs.save()
        
        form = CreateTaskForm(self.project, self.user, data = {'name':'Foo', 'start_date' : today_str, 'user_responsible':user.username})
        self.assertEqual(form.is_valid(), True)
        
        #Delte user, so we may reuse in other method
        user.delete()
        subs.delete()
        
    def testDates(self):
        "Start date can not be greater than end date"
        user = User.objects.create_user('demo', 'demo@gmail.com', 'demo')
        subs = SubscribedUser(user = user, project = self.project, group = 'Owner')
        subs.save()
        
        form = CreateTaskForm(self.project, self.user, data = {'name':'Foo', 'start_date' : today_str, 'end_date': str(datetime.date.min) ,'user_responsible':user.username})
        self.assertEqual(form.is_valid(), False)
        form = CreateTaskForm(self.project, self.user, data = {'name':'Foo', 'start_date' : today_str, 'end_date': str(datetime.date.max) ,'user_responsible':user.username})
        self.assertEqual(form.is_valid(), True)
        
        #Delte user, so we may reuse in other method
        user.delete()
        subs.delete()
        
    
        

        
import coverage
from django.test.simple import run_tests as django_test_runner
from django.conf import settings

def test_runner_with_coverage(test_labels, verbosity=1, interactive=True, extra_tests=[]):
    coverage.use_cache(0) # Do not cache any of the coverage.py stuff
    coverage.start()
    test_results = django_test_runner(test_labels, verbosity, interactive, extra_tests)
    coverage.stop()
    coverage_modules = []
    for module in settings.COVERAGE_MODULES:
        coverage_modules.append(__import__(module, globals(), locals(), ['']))
    coverage.report(coverage_modules, show_missing=0)
    return test_results


    
    
