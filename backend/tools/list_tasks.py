# backend/tools/list_tasks.py

from langchain.tools import tool
from zoho.client import ZohoClient
from typing import Optional

def make_list_tasks_tool(client: ZohoClient):
    @tool
    async def list_tasks(project_id: str, status: Optional[str] = None, assignee: Optional[str] = None) -> str:
        """List tasks for a project. Optionally filter by status or assignee."""
        data = await client.get(f"/portal/{client.portal_id}/projects/{project_id}/tasks/")
        tasks = data.get("tasks", [])
        if not tasks:
            return "No tasks found."

        # Apply filters
        if status:
            tasks = [t for t in tasks if t.get("status", {}).get("name", "").lower() == status.lower()]
        if assignee:
            tasks = [t for t in tasks if assignee.lower() in t.get("details", {}).get("owners", [{}])[0].get("name", "").lower()]

        return "\n".join([
            f"- [{t['id']}] {t['name']} | Status: {t.get('status', {}).get('name', 'N/A')} | Due: {t.get('end_date', 'N/A')}"
            for t in tasks
        ])
    return list_tasks