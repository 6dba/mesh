from .base import BaseNodeProvider
from typing import List, Dict, Any
import httpx

class AgentNodeProvider(BaseNodeProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_nodes(self) -> List[Dict[str, Any]]:
        # This might be used if the agent provides a list of sub-nodes, 
        # but usually it's one agent per node.
        return []

    async def sync_node(self, node_address: str) -> bool:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{node_address}/api/v1/status",
                    headers={"X-Kosatka-Key": self.api_key},
                    timeout=5.0
                )
                return response.status_code == 200
            except Exception:
                return False
