from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseAgentProvider(ABC):
    @abstractmethod
    async def get_clients(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def get_client(self, client_id: str) -> Dict[str, Any] | None:
        pass

    @abstractmethod
    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def delete_client(self, client_id: str) -> bool:
        pass

    @abstractmethod
    async def get_client_config(self, client_id: str) -> str:
        pass

    @abstractmethod
    async def get_client_stats(self, client_id: str) -> Dict[str, Any]:
        pass
