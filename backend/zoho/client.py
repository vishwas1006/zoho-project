import httpx
from auth.zoho_oauth import ZohoOAuth

class ZohoClient:
    BASE_URL = "https://projectsapi.zoho.com/restapi"

    def __init__(self, access_token: str, refresh_token: str, portal_id: str):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.portal_id = portal_id
        self.oauth = ZohoOAuth()

    def _headers(self):
        return {"Authorization": f"Zoho-oauthtoken {self.access_token}"}

    async def get(self, endpoint: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}{endpoint}",
                headers=self._headers()
            )
            if response.status_code == 401:
                await self._refresh()
                return await self.get(endpoint)
            return response.json()

    async def post(self, endpoint: str, data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}{endpoint}",
                headers=self._headers(),
                json=data
            )
            return response.json()

    async def _refresh(self):
        tokens = await self.oauth.refresh_access_token(self.refresh_token)
        self.access_token = tokens["access_token"]
        # Also update token in DB here