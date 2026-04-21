# backend/main.py

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from langchain_core.messages import HumanMessage

from auth.zoho_oauth import ZohoOAuth
from models.schemas import (
    ChatRequest, ChatResponse,
    ConfirmActionRequest, ConfirmActionResponse
)
from database import init_db, get_db, UserToken
from memory.long_term import long_term_memory
from memory.short_term import short_term_memory
from memory.pending_actions import pending_actions
from agents.graph import build_graph
from zoho.client import ZohoClient
import secrets

app = FastAPI()

# ─── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth = ZohoOAuth()

# ─── Startup ─────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    await init_db()


# ─── Auth Dependency ─────────────────────────────────────────
async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
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
async def callback(
    code: str,
    state: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    tokens = await oauth.exchange_code_for_tokens(code)
    if "access_token" not in tokens:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get tokens: {tokens}"
        )

    session_id = secrets.token_urlsafe(32)

    # Get portal ID
    temp_client = ZohoClient(
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token")
    )
    portal_id = await temp_client.get_portal_id()

    # Save to DB
    user_token = UserToken(
        session_id=session_id,
        access_token=tokens["access_token"],
        refresh_token=tokens.get("refresh_token"),
        portal_id=portal_id
    )
    db.add(user_token)
    await db.commit()

    response = JSONResponse({
        "message": "Login successful",
        "session_id": session_id,
        "portal_id": portal_id
    })
    response.set_cookie(
        key="session_id",
        value=session_id,
        httponly=True,
        samesite="lax"
    )
    return response


# ─── Chat Route ──────────────────────────────────────────────
@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    zoho_client = ZohoClient(
        access_token=user.access_token,
        refresh_token=user.refresh_token,
        portal_id=user.portal_id
    )

    graph = build_graph(zoho_client)

    config = {
        "configurable": {
            "thread_id": user.session_id
        }
    }

    # Get long-term context
    long_term_context = await long_term_memory.get_summary_for_user(
        db, user.session_id
    )

    # Build message with context
    user_message = request.message
    if long_term_context and long_term_context != "No previous context found.":
        user_message = (
            f"[Context from previous sessions:\n{long_term_context}]\n\n"
            f"User: {request.message}"
        )

    try:
        result = await graph.ainvoke(
            {"messages": [HumanMessage(content=user_message)]},
            config=config
        )

        last_message = result["messages"][-1]
        response_text = last_message.content

        # Check if HIL confirmation needed
        requires_confirmation = "do you confirm" in response_text.lower()
        confirmation_id = None

        if requires_confirmation:
            confirmation_id = pending_actions.save(
                session_id=user.session_id,
                action_type="write_operation",
                details={"message": request.message},
                graph_state=result
            )

        # Save to long-term memory
        await long_term_memory.save_message(
            db, user.session_id, user.session_id,
            "user", request.message
        )
        await long_term_memory.save_message(
            db, user.session_id, user.session_id,
            "assistant", response_text
        )

        return ChatResponse(
            message=response_text,
            agent_used=result.get("current_agent", "unknown"),
            requires_confirmation=requires_confirmation,
            confirmation_id=confirmation_id
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ─── Confirm/Cancel HIL Route ────────────────────────────────
@app.post("/chat/confirm", response_model=ConfirmActionResponse)
async def confirm_action(
    request: ConfirmActionRequest,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    pending = pending_actions.get(request.confirmation_id)

    if not pending:
        raise HTTPException(status_code=404, detail="No pending action found")

    if pending["session_id"] != user.session_id:
        raise HTTPException(status_code=403, detail="Not your action")

    if not request.confirmed:
        pending_actions.cancel(request.confirmation_id)
        pending_actions.delete(request.confirmation_id)
        return ConfirmActionResponse(
            message="❌ Action cancelled. Nothing was changed.",
            success=False
        )

    # User confirmed — resume graph
    zoho_client = ZohoClient(
        access_token=user.access_token,
        refresh_token=user.refresh_token,
        portal_id=user.portal_id
    )
    graph = build_graph(zoho_client)
    config = {"configurable": {"thread_id": user.session_id}}

    try:
        result = await graph.ainvoke(None, config=config)
        last_message = result["messages"][-1]
        pending_actions.delete(request.confirmation_id)

        return ConfirmActionResponse(
            message=last_message.content,
            success=True
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ─── Debug Portal ────────────────────────────────────────────
@app.get("/debug/portal")
async def debug_portal(user=Depends(get_current_user)):
    import httpx
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://projectsapi.zoho.in/restapi/portals/",
            headers={
                "Authorization": f"Zoho-oauthtoken {user.access_token}",
                "Accept": "application/json"
            }
        )
        return {
            "status": response.status_code,
            "body": response.text
        }


# ─── Health Check ────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "running"}