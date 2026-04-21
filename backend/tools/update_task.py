# backend/tools/update_task.py

from langchain.tools import tool
from zoho.client import ZohoClient
from typing import Optional

def make_update_task_tool(client: ZohoClient):
    @tool
    async def update_task(
        project_id: str,
        task_id: str,
        status: Optional[str] = None,
        assignee_id: Optional[str] = None,
        due_date: Optional[str] = None,
        priority: Optional[str] = None
    ) -> str:
        """Update a task's status, assignee, due date, or priority."""
        payload = {}
        if status:
            payload["status"] = status
        if assignee_id:
            payload["person_responsible"] = assignee_id
        if due_date:
            payload["end_date"] = due_date
        if priority:
            payload["priority"] = priority

        data = await client.patch(
            f"/portal/{client.portal_id}/projects/{project_id}/tasks/{task_id}/",
            payload
        )
        tasks = data.get("tasks", [])
        if tasks:
            return f" Task '{tasks[0]['name']}' updated successfully."
        return " Failed to update task."
    return update_task