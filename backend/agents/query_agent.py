# backend/agents/query_agent.py

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from config import settings


QUERY_SYSTEM_PROMPT = """You are a helpful project management assistant.
You help users READ information from their Zoho Projects account.

You can:
- List all projects
- List tasks in a project with filters
- Get full details of a task
- List project members and their roles
- Get task utilisation/workload summary per member

You CANNOT create, update, or delete anything.
If the user asks for a write operation, tell them you will route to the action agent.

Always be concise and clear. Format lists nicely.
When the user refers to "the first project" or "that project", 
use the context from previous messages to identify which project they mean.
"""


def create_query_agent(tools: list):
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        anthropic_api_key=settings.anthropic_api_key
    )

    agent = create_react_agent(
        model=llm,
        tools=tools,
        state_modifier=SystemMessage(content=QUERY_SYSTEM_PROMPT)
    )
    return agent