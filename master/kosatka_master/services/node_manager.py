from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..models.node import Node
from .providers.agent_provider import AgentNodeProvider


class NodeManager:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_node(
        self, name: str, address: str, provider_type: str = "agent", api_key: str | None = None
    ):
        node = Node(name=name, address=address, provider_type=provider_type, api_key=api_key)
        self.db.add(node)
        await self.db.commit()
        await self.db.refresh(node)
        return node

    async def sync_all_nodes(self):
        result = await self.db.execute(select(Node).where(Node.is_active.is_(True)))
        nodes = result.scalars().all()

        for node in nodes:
            # Use node's own key or global fallback
            key = node.api_key or settings.effective_agent_api_key()
            provider = AgentNodeProvider(key)
            is_up = await provider.sync_node(node.address)
            node.status = "online" if is_up else "offline"
            node.last_seen = datetime.now(timezone.utc).replace(tzinfo=None)

        await self.db.commit()
