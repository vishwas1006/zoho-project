# backend/main.py

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from auth.zoho_oauth import ZohoOAuth
from models.schemas import ChatRequest, ChatResponse
from database import init_db, get_db, UserToken

from memory.long_term import long_term_memory
from memory.short_term import short_term_memory
import secrets


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth = ZohoOAuth()

# ─── Create DB tables on startup ─────────────────────────────
@app.on_event("startup")
async def startup():
    await init_db()

# ─── Auth dependency ─────────────────────────────────────────
async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)):
    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    result = await db.execute(
        select(UserToken).where(UserToken.session_id == session_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=401, detail="Session expired")
    return user

# ─── Auth Routes ─────────────────────────────────────────────
@app.get("/auth/login")
async def login():
    state = secrets.token_urlsafe(16)
    url = oauth.get_authorization_url(state)
    return RedirectResponse(url)

@app.get("/auth/callback")
async def callback(code: str, request: Request, db: AsyncSession = Depends(get_db)):
    tokens = await oauth.exchange_code_for_tokens(code)

    if "access_token" not in tokens:
        raise HTTPException(status_code=400, detail="Failed to get tokens")

    # Save tokens to DB
    session_id = secrets.token_urlsafe(32)
    user_token = UserToken(
        session_id=session_id,
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
    )
    db.add(user_token)
    await db.commit()

    response = JSONResponse({"message": "Login successful", "session_id": session_id})
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return response

# ─── Chat Route ──────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user=Depends(get_current_user)):
    return ChatResponse(
        message=f"You said: {request.message}",
        agent_used="none",
        requires_confirmation=False
    )

# ─── Health Check ────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "running"}