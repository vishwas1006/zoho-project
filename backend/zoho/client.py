# backend/zoho/client.py

import httpx
from auth.zoho_oauth import ZohoOAuth


class ZohoClient:
    BASE_URL = "https://projectsapi.zoho.in/restapi"

    def __init__(self, access_token: str, refresh_token: str, portal_id: str = None):
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.portal_id = portal_id
        self.oauth = ZohoOAuth()
        self._refreshed = False

    def _headers(self):
        return {
            "Authorization": f"Zoho-oauthtoken {self.access_token}",
            "Content-Type": "application/json"
        }

    async def get(self, endpoint: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}{endpoint}",
                headers=self._headers()
            )
            print(f"GET {endpoint} → {response.status_code} | {response.text[:300]}")

            if not response.text.strip():
                return {}

            if response.status_code == 401 and not self._refreshed:
                self._refreshed = True
                await self._refresh()
                return await self.get(endpoint)

            self._refreshed = False
            return response.json()

    async def post(self, endpoint: str, data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}{endpoint}",
                headers=self._headers(),
                json=data
            )
            print(f"POST {endpoint} → {response.status_code} | {response.text[:300]}")

            if not response.text.strip():
                return {}

            return response.json()

    async def patch(self, endpoint: str, data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"{self.BASE_URL}{endpoint}",
                headers=self._headers(),
                json=data
            )
            print(f"PATCH {endpoint} → {response.status_code} | {response.text[:300]}")

            if not response.text.strip():
                return {}

            return response.json()

    async def delete(self, endpoint: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{self.BASE_URL}{endpoint}",
                headers=self._headers()
            )
            print(f"DELETE {endpoint} → {response.status_code} | {response.text[:300]}")

            if not response.text.strip():
                return {}

            return response.json()

    async def _refresh(self):
        tokens = await self.oauth.refresh_access_token(self.refresh_token)
        print(f"Refresh response: {tokens}")
        if "access_token" in tokens:
            self.access_token = tokens["access_token"]
        else:
            raise Exception(f"Token refresh failed: {tokens}")

    async def get_portal_id(self) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://projectsapi.zoho.in/restapi/portals/",
                headers={
                    "Authorization": f"Zoho-oauthtoken {self.access_token}",
                    "Accept": "application/json"
                }
            )
            print(f"Portal response: {response.status_code} | {response.text[:300]}")

            if not response.text.strip():
                raise Exception("Empty portal response")

            data = response.json()
            portals = data.get("portals", [])
            if portals:
                self.portal_id = str(portals[0]["id"])
                print(f"Portal ID: {self.portal_id}")
                return self.portal_id

            raise Exception(f"No portals found: {data}")