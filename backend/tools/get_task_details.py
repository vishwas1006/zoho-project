# backend/tools/get_task_details.py

from langchain.tools import tool
from zoho.client import ZohoClient

def make_get_task_details_tool(client: ZohoClient):
    @tool
    async def get_task_details(project_id: str, task_id: str) -> str:
        """Get full details of a single task by ID."""
        data = await client.get(f"/portal/{client.portal_id}/projects/{project_id}/tasks/{task_id}/")
        tasks = data.get("tasks", [])
        if not tasks:
            return "Task not found."
        t = tasks[0]
        return (
            f"Task: {t['name']}\n"
            f"ID: {t['id']}\n"
            f"Status: {t.get('status', {}).get('name', 'N/A')}\n"
            f"Priority: {t.get('priority', 'N/A')}\n"
            f"Due Date: {t.get('end_date', 'N/A')}\n"
            f"Assignee: {t.get('details', {}).get('owners', [{}])[0].get('name', 'N/A')}\n"
            f"Description: {t.get('description', 'N/A')}"
        )
    return get_task_details