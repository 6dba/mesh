from .base import BaseAgentProvider
from typing import List, Dict, Any
import httpx

class MarzbanProvider(BaseAgentProvider):
    def __init__(self, url: str, username: str, password: str):
        self.url = url
        self.username = username
        self.password = password
        self.token = None

    async def _get_token(self):
        if self.token:
            return self.token
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.url}/api/admin/token",
                data={"username": self.username, "password": self.password}
            )
            resp.raise_for_status()
            self.token = resp.json()["access_token"]
            return self.token

    async def get_clients(self) -> List[Dict[str, Any]]:
        # TODO: Implement Marzban API call
        return []

    async def get_client(self, client_id: str) -> Dict[str, Any] | None:
        return None

    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"id": client_data.get("username"), "status": "created"}

    async def delete_client(self, client_id: str) -> bool:
        return True

    async def get_client_config(self, client_id: str) -> str:
        return "vless://..."

    async def get_client_stats(self, client_id: str) -> Dict[str, Any]:
        return {"usage": 0}
