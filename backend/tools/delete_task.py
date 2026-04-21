# backend/tools/delete_task.py

from langchain.tools import tool
from zoho.client import ZohoClient

def make_delete_task_tool(client: ZohoClient):
    @tool
    async def delete_task(project_id: str, task_id: str) -> str:
        """Delete a task. Requires explicit user confirmation before executing."""
        data = await client.delete(
            f"/portal/{client.portal_id}/projects/{project_id}/tasks/{task_id}/"
        )
        if data.get("response", {}).get("status") == "success":
            return f"✅ Task {task_id} deleted successfully."
        return "❌ Failed to delete task."
    return delete_task