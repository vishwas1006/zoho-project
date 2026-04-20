# agents/router.py
from langchain_anthropic import ChatAnthropic

def create_router(llm):
    def route(state):
        message = state["messages"][-1].content.lower()
        # Simple keyword routing
        write_keywords = ["create", "update", "delete", "assign"]
        if any(word in message for word in write_keywords):
            return "action_agent"
        return "query_agent"
    return route