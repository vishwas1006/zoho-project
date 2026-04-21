# backend/agents/action_agent.py

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent
from config import settings


ACTION_SYSTEM_PROMPT = """You are a project management assistant handling WRITE operations.

You can:
- Create new tasks
- Update task status, assignee, due date, or priority
- Delete tasks

IMPORTANT RULES:
1. Before executing ANY operation, always summarise exactly what you are about to do
2. Wait for explicit user confirmation before proceeding
3. If the user says no, cancel and confirm cancellation
4. Never execute write operations without confirmation

Format your confirmation request like this:
---
⚠️ I am about to:
[ACTION]: [DETAILS]

Do you confirm? (yes/no)
---
"""


def create_action_agent(tools: list):
    llm = ChatAnthropic(
        model="claude-3-5-sonnet-20241022",
        anthropic_api_key=settings.anthropic_api_key
    )

    agent = create_react_agent(
        model=llm,
        tools=tools,
        state_modifier=SystemMessage(content=ACTION_SYSTEM_PROMPT),
        interrupt_before=["tools"]   # ← This is the HIL pause
    )
    return agent