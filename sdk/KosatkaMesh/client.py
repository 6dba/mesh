import logging
from typing import Any, Dict, List, Optional

import httpx

from .exceptions import KosatkaAPIError, KosatkaAuthError, KosatkaValidationError
from .models import Client, Node, NodeCreate, ProvisionRequest, Subscription, SubscriptionCreate

logger = logging.getLogger(__name__)


class MeshClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {"X-Kosatka-Key": self.api_key, "Content-Type": "application/json"}

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}/api/v1{path}"
        async with httpx.AsyncClient(headers=self.headers) as client:
            try:
                response = await client.request(method, url, timeout=self.timeout, **kwargs)

                if response.status_code == 401:
                    raise KosatkaAuthError(status_code=401, detail="Invalid API Key")
                if response.status_code == 422:
                    raise KosatkaValidationError(response.text)
                if response.status_code >= 400:
                    raise KosatkaAPIError(status_code=response.status_code, detail=response.text)

                return response.json()
            except (KosatkaAPIError, KosatkaValidationError):
                raise
            except Exception as e:
                logger.error(f"Request failed: {e}")
                raise KosatkaAPIError(status_code=500, detail=f"Connection failed: {str(e)}") from e

    # ─── Nodes ─────────────────────────────────────────────────────────
    async def list_nodes(self) -> List[Node]:
        data = await self._request("GET", "/nodes")
        return [Node.model_validate(n) for n in data]

    async def register_node(self, node_in: NodeCreate) -> Node:
        data = await self._request("POST", "/nodes", json=node_in.model_dump())
        return Node.model_validate(data)

    async def get_node_health(self, node_id: int) -> Dict[str, Any]:
        return await self._request("GET", f"/nodes/{node_id}/health")

    # ─── Clients ───────────────────────────────────────────────────────
    async def provision(
        self,
        name: str,
        protocol: str = "awg",
        email: Optional[str] = None,
        node_id: Optional[int] = None,
    ) -> Client:
        """Create-or-get a client and materialize a VPN peer on a matching node.

        Returns a Client enriched with `config_text` (the ready-to-import
        wg/awg config) plus `address`, `public_key`, `node_id` and
        `provider_type`. `name` is used as `external_id` — pass a stable
        per-user identifier (e.g. your internal user id).
        """
        payload = ProvisionRequest(
            external_id=name, email=email, protocol=protocol, node_id=node_id
        )
        data = await self._request(
            "POST", "/clients/provision", json=payload.model_dump(exclude_none=True)
        )
        return Client.model_validate(data)

    async def create_client(self, external_id: str, email: Optional[str] = None) -> Client:
        """Create a bare Client DB row without provisioning a VPN peer."""
        data = await self._request(
            "POST", "/clients", json={"external_id": external_id, "email": email}
        )
        return Client.model_validate(data)

    async def get_client(self, client_id: int) -> Client:
        data = await self._request("GET", f"/clients/{client_id}")
        return Client.model_validate(data)

    async def get_client_config(self, external_id: str, node_id: Optional[int] = None) -> str:
        """Fetch the current running config text for a previously provisioned client."""
        params: Dict[str, Any] = {}
        if node_id is not None:
            params["node_id"] = node_id
        data = await self._request(
            "GET", f"/clients/by-external/{external_id}/config", params=params
        )
        return data.get("config", "") or data.get("config_text", "") or ""

    async def revoke(self, client_id: int) -> None:
        await self._request("DELETE", f"/clients/{client_id}")

    # ─── Subscriptions ────────────────────────────────────────────────
    async def create_subscription(self, sub_in: SubscriptionCreate) -> Subscription:
        data = await self._request("POST", "/subscriptions", json=sub_in.model_dump())
        return Subscription.model_validate(data)

    async def get_client_subscriptions(self, client_id: int) -> List[Subscription]:
        data = await self._request("GET", f"/clients/{client_id}/subscriptions")
        return [Subscription.model_validate(s) for s in data]
