import asyncio
from typing import Any, Dict, List

from .base import BaseAgentProvider


class AmneziaWGProvider(BaseAgentProvider):
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.lock = asyncio.Lock()

    async def get_clients(self) -> List[Dict[str, Any]]:
        return []

    async def get_client(self, client_id: str) -> Dict[str, Any] | None:
        return None

    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        async with self.lock:
            return {"id": client_data.get("external_id"), "status": "added"}

    async def delete_client(self, client_id: str) -> bool:
        async with self.lock:
            return True

    async def get_client_config(self, client_id: str) -> str:
        return "AmneziaWG Config Content"

    async def get_client_stats(self, client_id: str) -> Dict[str, Any]:
        return {"transfer_rx": 0, "transfer_tx": 0}
