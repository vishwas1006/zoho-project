# backend/models/schemas.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# ─── Auth Schemas ───────────────────────────────────────────

class TokenData(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


class UserSession(BaseModel):
    user_id: str
    session_id: str
    portal_id: str
    access_token: str
    refresh_token: str
    created_at: datetime = datetime.now()


# ─── Chat Schemas ────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    agent_used: Optional[str] = None      # "query_agent" or "action_agent"
    requires_confirmation: bool = False    # True when HIL is triggered
    confirmation_id: Optional[str] = None # ID to confirm/cancel the action


class ConfirmActionRequest(BaseModel):
    confirmation_id: str
    confirmed: bool   # True = proceed, False = cancel


class ConfirmActionResponse(BaseModel):
    message: str
    success: bool


# ─── Zoho Project Schemas ────────────────────────────────────

class Project(BaseModel):
    id: str
    name: str
    status: Optional[str] = None
    owner: Optional[str] = None


class Task(BaseModel):
    id: str
    name: str
    status: Optional[str] = None
    assignee: Optional[str] = None
    due_date: Optional[str] = None
    priority: Optional[str] = None
    project_id: Optional[str] = None


class ProjectMember(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    role: Optional[str] = None


# ─── Memory Schemas ──────────────────────────────────────────

class UserPreference(BaseModel):
    user_id: str
    key: str
    value: str
    updated_at: datetime = datetime.now()


class ConversationHistory(BaseModel):
    user_id: str
    session_id: str
    role: str          # "user" or "assistant"
    content: str
    timestamp: datetime = datetime.now()