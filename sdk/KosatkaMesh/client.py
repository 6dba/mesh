import logging
from typing import Any, Dict, List

import httpx

from .exceptions import KosatkaAPIError, KosatkaAuthError, KosatkaValidationError
from .models import Client, Node, NodeCreate, Subscription, SubscriptionCreate

logger = logging.getLogger(__name__)


class MeshClient:
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {"X-Kosatka-Key": self.api_key, "Content-Type": "application/json"}

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}/api/v1{path}"
        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.request(method, url, timeout=10.0, **kwargs)

                if response.status_code == 401:
                    raise KosatkaAuthError(status_code=401, detail="Invalid API Key")
                if response.status_code == 422:
                    raise KosatkaValidationError(response.text)
                if response.status_code >= 400:
                    raise KosatkaAPIError(status_code=response.status_code, detail=response.text)

                return response.json()
            except Exception as e:
                if isinstance(e, (KosatkaAPIError, KosatkaValidationError)):
                    raise
                logger.error(f"Request failed: {e}")
                raise KosatkaAPIError(status_code=500, detail=f"Connection failed: {str(e)}")

    # Nodes
    async def list_nodes(self) -> List[Node]:
        data = await self._request("GET", "/nodes")
        return [Node.model_validate(n) for n in data]

    async def register_node(self, node_in: NodeCreate) -> Node:
        data = await self._request("POST", "/nodes", json=node_in.model_dump())
        return Node.model_validate(data)

    async def get_node_health(self, node_id: int) -> Dict[str, Any]:
        return await self._request("GET", f"/nodes/{node_id}/health")

    # Clients
    async def provision(self, name: str, protocol: str) -> Client:
        data = await self._request("POST", "/clients", json={"name": name, "protocol": protocol})
        return Client.model_validate(data)

    async def get_client(self, client_id: int) -> Client:
        data = await self._request("GET", f"/clients/{client_id}")
        return Client.model_validate(data)

    async def revoke(self, client_id: int):
        await self._request("DELETE", f"/clients/{client_id}")

    # Subscriptions
    async def create_subscription(self, sub_in: SubscriptionCreate) -> Subscription:
        data = await self._request("POST", "/subscriptions", json=sub_in.model_dump())
        return Subscription.model_validate(data)

    async def get_client_subscriptions(self, client_id: int) -> List[Subscription]:
        data = await self._request("GET", f"/clients/{client_id}/subscriptions")
        return [Subscription.model_validate(s) for s in data]
