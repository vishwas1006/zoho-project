# backend/agents/router.py

from langchain_core.messages import HumanMessage


class Router:
    """Decides which agent handles the incoming message."""

    WRITE_KEYWORDS = [
        "create", "add", "new task",
        "update", "change", "edit", "modify",
        "delete", "remove",
        "assign", "reassign"
    ]

    def route(self, state: dict) -> str:
        """Returns 'action_agent' or 'query_agent'."""
        messages = state.get("messages", [])
        if not messages:
            return "query_agent"

        last_message = messages[-1]
        content = (
            last_message.content
            if hasattr(last_message, "content")
            else str(last_message)
        ).lower()

        if any(keyword in content for keyword in self.WRITE_KEYWORDS):
            return "action_agent"
        return "query_agent"


router = Router()