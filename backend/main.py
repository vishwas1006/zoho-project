from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from auth.zoho_oauth import ZohoOAuth
import secrets
from models.schemas import ChatRequest, ChatResponse

app = FastAPI()
oauth = ZohoOAuth()

@app.get("/auth/login")
async def login():
    state = secrets.token_urlsafe(16)
    url = oauth.get_authorization_url(state)
    return RedirectResponse(url)

@app.get("/auth/callback")
async def callback(code: str, request: Request):
    tokens = await oauth.exchange_code_for_tokens(code)
    # Save tokens to DB, create session
    # Redirect to frontend
    return {"tokens": tokens}  # temporary



@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, user=Depends(get_current_user)):
    config = {"configurable": {"thread_id": user.session_id}}
    result = await graph.ainvoke(
        {"messages": [{"role": "user", "content": request.message}]},
        config=config
    )
    return ChatResponse(message=result["messages"][-1].content)