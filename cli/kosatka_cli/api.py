import httpx
from typing import Any, Optional, List, Dict
from .config import load_config

class APIClient:
    def __init__(self):
        self.config = load_config()
        self.headers = {
            "X-Kosatka-Key": self.config.api_key,
            "Content-Type": "application/json"
        }

    def _get_url(self, path: str) -> str:
        return f"{self.config.base_url.rstrip('/')}/api/v1{path}"

    async def request(self, method: str, path: str, **kwargs) -> Any:
        url = self._get_url(path)
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.request(method, url, timeout=10.0, **kwargs)
            response.raise_for_status()
            return response.json()

    async def list_nodes(self) -> List[Dict[str, Any]]:
        return await self.request("GET", "/nodes")

    async def register_node(self, name: str, address: str, provider_type: str = "agent") -> Dict[str, Any]:
        data = {
            "name": name,
            "address": address,
            "provider_type": provider_type
        }
        return await self.request("POST", "/nodes", json=data)

    async def provision_client(self, name: str, protocol: str) -> Dict[str, Any]:
        data = {
            "name": name,
            "protocol": protocol
        }
        return await self.request("POST", "/clients", json=data)

    async def get_node_health(self, node_id: int) -> Dict[str, Any]:
        return await self.request("GET", f"/nodes/{node_id}/health")

    async def get_stats(self) -> Dict[str, Any]:
        return await self.request("GET", "/stats/summary")
