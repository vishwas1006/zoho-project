# backend/tools/create_task.py

from langchain.tools import tool
from zoho.client import ZohoClient

def make_create_task_tool(client: ZohoClient):
    @tool
    async def create_task(project_id: str, name: str, description: str = "", due_date: str = "") -> str:
        """Create a new task in a given project. Requires confirmation before executing."""
        payload = {"name": name}
        if description:
            payload["description"] = description
        if due_date:
            payload["end_date"] = due_date

        data = await client.post(
            f"/portal/{client.portal_id}/projects/{project_id}/tasks/",
            payload
        )
        tasks = data.get("tasks", [])
        if tasks:
            return f"✅ Task '{tasks[0]['name']}' created successfully with ID: {tasks[0]['id']}"
        return "❌ Failed to create task."
    return create_task