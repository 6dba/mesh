from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel
from kosatka_master.database import get_db
from kosatka_master.models.node import Node
from kosatka_master.security import get_api_key

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
