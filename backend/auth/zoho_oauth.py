# backend/auth/zoho_oauth.py

import httpx
from config import settings


class ZohoOAuth:
    AUTH_URL = "https://accounts.zoho.in/oauth/v2/auth"
    TOKEN_URL = "https://accounts.zoho.in/oauth/v2/token"
    SCOPES = "ZohoProjects.projects.READ,ZohoProjects.tasks.ALL,ZohoProjects.users.READ,ZohoProjects.portals.READ"

    def get_authorization_url(self, state: str) -> str:
        params = {
            "response_type": "code",
            "client_id": settings.zoho_client_id,
            "scope": self.SCOPES,
            "redirect_uri": settings.zoho_redirect_uri,
            "access_type": "offline",
            "state": state
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{self.AUTH_URL}?{query}"

    async def exchange_code_for_tokens(self, code: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.zoho_client_id,
                    "client_secret": settings.zoho_client_secret,
                    "redirect_uri": settings.zoho_redirect_uri,
                    "grant_type": "authorization_code"
                }
            )
            data = response.json()
            print("Token response:", data)
            return data

    async def refresh_access_token(self, refresh_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.TOKEN_URL,
                data={
                    "refresh_token": refresh_token,
                    "client_id": settings.zoho_client_id,
                    "client_secret": settings.zoho_client_secret,
                    "grant_type": "refresh_token"
                }
            )
            data = response.json()
            print("Refresh response:", data)
            return data