# backend/tools/get_task_utilisation.py

from langchain.tools import tool
from zoho.client import ZohoClient
from collections import defaultdict

def make_get_task_utilisation_tool(client: ZohoClient):
    @tool
    async def get_task_utilisation(project_id: str) -> str:
        """Summarise task load per member across a project."""
        data = await client.get(f"/portal/{client.portal_id}/projects/{project_id}/tasks/")
        tasks = data.get("tasks", [])
        if not tasks:
            return "No tasks found."

        # Count tasks per member
        member_tasks = defaultdict(list)
        for task in tasks:
            owners = task.get("details", {}).get("owners", [])
            for owner in owners:
                name = owner.get("name", "Unassigned")
                member_tasks[name].append(task["name"])

        if not member_tasks:
            return "No assigned tasks found."

        result = " Task load per member:\n"
        for member, tasks_list in sorted(member_tasks.items(), key=lambda x: -len(x[1])):
            result += f"\n {member}: {len(tasks_list)} tasks\n"
            for t in tasks_list[:3]:  # show first 3
                result += f"   - {t}\n"
            if len(tasks_list) > 3:
                result += f"   ... and {len(tasks_list) - 3} more\n"
        return result
    return get_task_utilisation