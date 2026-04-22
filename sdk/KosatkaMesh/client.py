import httpx
from typing import List, Optional, Any, Dict
from .models import (
    Node, NodeCreate, 
    Client, ClientCreate, 
    Subscription, SubscriptionCreate
)
from .exceptions import KosatkaAPIError, KosatkaAuthError

class MeshClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.headers = {
            "X-Kosatka-Key": api_key,
            "Content-Type": "application/json",
            "X-SDK-Version": "0.1.0"
        }
        self.timeout = timeout

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}/api/v1{path}"
        async with httpx.AsyncClient(headers=self.headers, timeout=self.timeout) as client:
            try:
                response = await client.request(method, url, **kwargs)
                
                if response.status_code == 401:
                    raise KosatkaAuthError(401, "Invalid API Key")
                
                if response.status_code >= 400:
                    try:
                        detail = response.json().get("detail", response.text)
                    except:
                        detail = response.text
                    raise KosatkaAPIError(response.status_code, detail)
                
                return response.json()
            except httpx.RequestError as e:
                raise KosatkaAPIError(0, f"Network error: {str(e)}")

    # Nodes
    async def list_nodes(self) -> List[Node]:
        data = await self._request("GET", "/nodes")
        return [Node.model_validate(n) for n in data]

    async def get_node(self, node_id: int) -> Node:
        data = await self._request("GET", f"/nodes/{node_id}")
        return Node.model_validate(data)

    async def register_node(self, node_in: NodeCreate) -> Node:
        data = await self._request("POST", "/nodes", json=node_in.model_dump())
        return Node.model_validate(data)

    async def get_node_health(self, node_id: int) -> Dict[str, Any]:
        return await self._request("GET", f"/nodes/{node_id}/health")

    # Clients
    async def create_client(self, client_in: ClientCreate) -> Client:
        data = await self._request("POST", "/clients", json=client_in.model_dump())
        return Client.model_validate(data)

    async def get_client(self, external_id: str) -> Client:
        data = await self._request("GET", f"/clients/{external_id}")
        return Client.model_validate(data)

    # Subscriptions
    async def create_subscription(self, sub_in: SubscriptionCreate) -> Subscription:
        data = await self._request("POST", "/subscriptions", json=sub_in.model_dump())
        return Subscription.model_validate(data)

    async def get_client_subscriptions(self, client_id: int) -> List[Subscription]:
        data = await self._request("GET", f"/clients/{client_id}/subscriptions")
        return [Subscription.model_validate(s) for s in data]
