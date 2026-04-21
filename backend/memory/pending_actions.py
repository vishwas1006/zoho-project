# backend/memory/pending_actions.py

from typing import Optional
import uuid


class PendingActionsStore:
    """
    Stores write operations that are waiting for
    human confirmation before executing.
    """

    def __init__(self):
        self._store: dict = {}

    def save(
        self,
        session_id: str,
        action_type: str,
        details: dict,
        graph_state: dict
    ) -> str:
        """Save a pending action and return its confirmation ID."""
        confirmation_id = str(uuid.uuid4())
        self._store[confirmation_id] = {
            "session_id": session_id,
            "action_type": action_type,
            "details": details,
            "graph_state": graph_state,
            "confirmed": None
        }
        return confirmation_id

    def get(self, confirmation_id: str) -> Optional[dict]:
        """Get a pending action by ID."""
        return self._store.get(confirmation_id)

    def confirm(self, confirmation_id: str) -> bool:
        """Mark action as confirmed."""
        if confirmation_id in self._store:
            self._store[confirmation_id]["confirmed"] = True
            return True
        return False

    def cancel(self, confirmation_id: str) -> bool:
        """Mark action as cancelled."""
        if confirmation_id in self._store:
            self._store[confirmation_id]["confirmed"] = False
            return True
        return False

    def delete(self, confirmation_id: str):
        """Remove action after it's been handled."""
        self._store.pop(confirmation_id, None)


# Singleton instance
pending_actions = PendingActionsStore()