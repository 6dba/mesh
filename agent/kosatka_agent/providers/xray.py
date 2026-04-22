from typing import Any, Dict, List

from .base import BaseAgentProvider


class XrayProvider(BaseAgentProvider):
    async def get_clients(self) -> List[Dict[str, Any]]:
        return []

    async def get_client(self, client_id: str) -> Dict[str, Any] | None:
        return None

    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"id": client_data.get("id"), "status": "created"}

    async def delete_client(self, client_id: str) -> bool:
        return True

    async def get_client_config(self, client_id: str) -> str:
        return ""

    async def get_client_stats(self, client_id: str) -> Dict[str, Any]:
        return {"id": client_id, "up": 0, "down": 0}
