# backend/tools/list_projects.py

from langchain.tools import tool
from zoho.client import ZohoClient

def make_list_projects_tool(client: ZohoClient):
    @tool
    async def list_projects() -> str:
        """List all Zoho projects for the current user."""
        data = await client.get(f"/portal/{client.portal_id}/projects/")
        projects = data.get("projects", [])
        if not projects:
            return "No projects found."
        return "\n".join([
            f"- {p['name']} (ID: {p['id']}, Status: {p.get('status', 'N/A')})"
            for p in projects
        ])
    return list_projects