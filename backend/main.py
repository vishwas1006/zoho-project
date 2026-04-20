from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from auth.zoho_oauth import ZohoOAuth
import secrets

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