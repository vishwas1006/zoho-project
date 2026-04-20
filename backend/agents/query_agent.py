# agents/query_agent.py
from langgraph.prebuilt import create_react_agent

def create_query_agent(llm, tools):
    query_tools = [
        tools["list_projects"],
        tools["list_tasks"],
        tools["get_task_details"],
        tools["list_project_members"],
        tools["get_task_utilisation"]
    ]
    return create_react_agent(llm, query_tools)