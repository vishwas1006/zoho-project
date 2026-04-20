# backend/main.py

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from auth.zoho_oauth import ZohoOAuth
from models.schemas import ChatRequest, ChatResponse
import secrets

app = FastAPI()

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth = ZohoOAuth()

# ─── Simple session store (replace with DB later) ────────────
sessions = {}  # session_id -> user data

# ─── Auth dependency ─────────────────────────────────────────
async def get_current_user(request: Request):
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in sessions:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return sessions[session_id]

# ─── Auth Routes ─────────────────────────────────────────────
@app.get("/auth/login")
async def login():
    state = secrets.token_urlsafe(16)
    url = oauth.get_authorization_url(state)
    return RedirectResponse(url)

@app.get("/auth/callback")
async def callback(code: str, request: Request):
    tokens = await oauth.exchange_code_for_tokens(code)

    if "access_token" not in tokens:
        raise HTTPException(status_code=400, detail="Failed to get tokens")

    # Create session
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = {
        "access_token": tokens["access_token"],
        "refresh_token": tokens.get("refresh_token"),
        "session_id": session_id
    }

    response = JSONResponse({"message": "Login successful"})
    response.set_cookie(key="session_id", value=session_id, httponly=True)
    return response

# ─── Chat Route ──────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user=Depends(get_current_user)):
    # Placeholder — agents will be wired here later
    return ChatResponse(
        message=f"You said: {request.message}",
        agent_used="none",
        requires_confirmation=False
    )

# ─── Health Check ────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "running"}