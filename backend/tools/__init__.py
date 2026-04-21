# backend/tools/__init__.py

from tools.list_projects import make_list_projects_tool
from tools.list_tasks import make_list_tasks_tool
from tools.get_task_details import make_get_task_details_tool
from tools.create_task import make_create_task_tool
from tools.update_task import make_update_task_tool
from tools.delete_task import make_delete_task_tool
from tools.list_project_members import make_list_project_members_tool
from tools.get_task_utilisation import make_get_task_utilisation_tool

def make_all_tools(client):
    return {
        "list_projects": make_list_projects_tool(client),
        "list_tasks": make_list_tasks_tool(client),
        "get_task_details": make_get_task_details_tool(client),
        "create_task": make_create_task_tool(client),
        "update_task": make_update_task_tool(client),
        "delete_task": make_delete_task_tool(client),
        "list_project_members": make_list_project_members_tool(client),
        "get_task_utilisation": make_get_task_utilisation_tool(client),
    }