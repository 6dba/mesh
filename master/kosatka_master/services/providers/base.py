from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseNodeProvider(ABC):
    @abstractmethod
    async def get_nodes(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def sync_node(self, node_id: str) -> bool:
        pass
