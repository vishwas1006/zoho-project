# backend/tools/list_project_members.py

from langchain.tools import tool
from zoho.client import ZohoClient

def make_list_project_members_tool(client: ZohoClient):
    @tool
    async def list_project_members(project_id: str) -> str:
        """Get all members of a project with their roles."""
        data = await client.get(f"/portal/{client.portal_id}/projects/{project_id}/users/")
        users = data.get("users", [])
        if not users:
            return "No members found."
        return "\n".join([
            f"- {u['name']} | Role: {u.get('role', 'N/A')} | Email: {u.get('email', 'N/A')}"
            for u in users
        ])
    return list_project_members