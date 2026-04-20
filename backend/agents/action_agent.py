# agents/action_agent.py
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

def create_action_agent(llm, tools):
    action_tools = [
        tools["create_task"],
        tools["update_task"],
        tools["delete_task"]
    ]
    # interrupt_before pauses for human confirmation
    return create_react_agent(
        llm, 
        action_tools,
        interrupt_before=["tools"]
    )