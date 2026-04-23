from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException
from kosatka_master.config import settings
from kosatka_master.database import get_db
from kosatka_master.models.node import Node
from kosatka_master.security import get_api_key
from kosatka_master.services.providers.agent_provider import AgentNodeProvider
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/nodes", tags=["nodes"], dependencies=[Depends(get_api_key)])


class NodeSchema(BaseModel):
    id: int
    name: str
    address: str
    provider_type: str
    status: str
    is_active: bool

    class Config:
        from_attributes = True


class NodeCreate(BaseModel):
    name: str
    address: str
    provider_type: str = "agent"


@router.get("/", response_model=List[NodeSchema])
async def get_nodes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Node))
    return result.scalars().all()


@router.post("/", response_model=NodeSchema)
async def create_node(node_data: NodeCreate, db: AsyncSession = Depends(get_db)):
    node = Node(**node_data.model_dump())
    db.add(node)
    await db.commit()
    await db.refresh(node)
    return node


@router.delete("/{node_id}")
async def delete_node(node_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Node).where(Node.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    await db.delete(node)
    await db.commit()
    return {"status": "success"}


@router.get("/{node_id}/health")
async def get_node_health(node_id: int, db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """Probe agent health live. The SDK and CLI both call this endpoint."""
    result = await db.execute(select(Node).where(Node.id == node_id))
    node = result.scalar_one_or_none()
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")

    provider = AgentNodeProvider(settings.effective_agent_api_key())
    is_up = await provider.sync_node(node.address)
    return {
        "id": node.id,
        "name": node.name,
        "address": node.address,
        "status": "online" if is_up else "offline",
        "provider_type": node.provider_type,
    }
