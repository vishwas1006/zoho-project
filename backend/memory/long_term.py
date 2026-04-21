# backend/memory/long_term.py

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Column, String, DateTime, Text, select, delete
from database import Base, engine
from datetime import datetime
import json


# ─── DB Tables ───────────────────────────────────────────────

class UserPreferenceModel(Base):
    __tablename__ = "user_preferences"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    key = Column(String, nullable=False)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ConversationHistoryModel(Base):
    __tablename__ = "conversation_history"

    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    session_id = Column(String, nullable=False)
    role = Column(String, nullable=False)   # "user" or "assistant"
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.now)


# ─── Long Term Memory Class ───────────────────────────────────

class LongTermMemory:

    # ── Preferences ──────────────────────────────────────────

    async def save_preference(
        self,
        db: AsyncSession,
        user_id: str,
        key: str,
        value: any
    ):
        """Save a user preference (e.g. favourite project)."""
        import uuid
        existing = await db.execute(
            select(UserPreferenceModel).where(
                UserPreferenceModel.user_id == user_id,
                UserPreferenceModel.key == key
            )
        )
        record = existing.scalar_one_or_none()

        if record:
            record.value = json.dumps(value)
            record.updated_at = datetime.now()
        else:
            db.add(UserPreferenceModel(
                id=str(uuid.uuid4()),
                user_id=user_id,
                key=key,
                value=json.dumps(value)
            ))
        await db.commit()

    async def get_preference(
        self,
        db: AsyncSession,
        user_id: str,
        key: str
    ) -> any:
        """Get a specific user preference."""
        result = await db.execute(
            select(UserPreferenceModel).where(
                UserPreferenceModel.user_id == user_id,
                UserPreferenceModel.key == key
            )
        )
        record = result.scalar_one_or_none()
        if record:
            return json.loads(record.value)
        return None

    async def get_all_preferences(
        self,
        db: AsyncSession,
        user_id: str
    ) -> dict:
        """Get all preferences for a user."""
        result = await db.execute(
            select(UserPreferenceModel).where(
                UserPreferenceModel.user_id == user_id
            )
        )
        records = result.scalars().all()
        return {r.key: json.loads(r.value) for r in records}

    # ── Conversation History ──────────────────────────────────

    async def save_message(
        self,
        db: AsyncSession,
        user_id: str,
        session_id: str,
        role: str,
        content: str
    ):
        """Save a message to conversation history."""
        import uuid
        db.add(ConversationHistoryModel(
            id=str(uuid.uuid4()),
            user_id=user_id,
            session_id=session_id,
            role=role,
            content=content
        ))
        await db.commit()

    async def get_recent_history(
        self,
        db: AsyncSession,
        user_id: str,
        limit: int = 10
    ) -> list:
        """Get last N messages for a user across sessions."""
        result = await db.execute(
            select(ConversationHistoryModel)
            .where(ConversationHistoryModel.user_id == user_id)
            .order_by(ConversationHistoryModel.timestamp.desc())
            .limit(limit)
        )
        records = result.scalars().all()
        return [
            {"role": r.role, "content": r.content, "timestamp": str(r.timestamp)}
            for r in reversed(records)
        ]

    async def get_summary_for_user(
        self,
        db: AsyncSession,
        user_id: str
    ) -> str:
        """Build a context summary for returning users."""
        prefs = await self.get_all_preferences(db, user_id)
        history = await self.get_recent_history(db, user_id, limit=5)

        summary = ""

        if prefs:
            summary += "User preferences:\n"
            for k, v in prefs.items():
                summary += f"- {k}: {v}\n"

        if history:
            summary += "\nRecent conversation:\n"
            for msg in history:
                summary += f"- {msg['role']}: {msg['content'][:100]}\n"

        return summary if summary else "No previous context found."


# ─── Singleton instance ───────────────────────────────────────
long_term_memory = LongTermMemory()