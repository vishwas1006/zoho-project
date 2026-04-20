# backend/database.py

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import Column, String, DateTime
from datetime import datetime

DATABASE_URL = "sqlite+aiosqlite:///./chatbot.db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

# ─── User Token Table ─────────────────────────────────────────
class UserToken(Base):
    __tablename__ = "user_tokens"

    session_id = Column(String, primary_key=True)
    user_id = Column(String, nullable=True)
    access_token = Column(String, nullable=False)
    refresh_token = Column(String, nullable=True)
    portal_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# ─── Create tables ────────────────────────────────────────────
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# ─── Get DB session ───────────────────────────────────────────
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session