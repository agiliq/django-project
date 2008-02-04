def project_tasks(request, project_name):
    """Displays all the top tasks and task items for a specific project.
    shows top tasks
    shows sub tasks name for top tasks
    shows task items for the top tasks
    """
    pass

def task_details(request, project_name, task_num):
    """Shows details ofa specific task.
    Shows a specific task.
    Shows its subtasks.
    Shows taskitems.
    Shows notes on the tasks.
    Shows form to add sub task.
    Shows form to add task items.
    Shows notes on taskitems.(?)
    """    
    pass

def task_history(request, project_name, task_num):
    """
    Shows tasks history for given task.
    Allows to rol back to a specific revisiosn of the task.
    """
    pass

def taskitem_history(request, project_name, taskitem_num):
    """Shows taskitem history for a given item.
    Allows to rollback to a specific version."""
    pass
