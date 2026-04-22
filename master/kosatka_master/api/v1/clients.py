from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from kosatka_master.database import get_db
from kosatka_master.models.client import Client
from kosatka_master.security import get_api_key
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/clients", tags=["clients"], dependencies=[Depends(get_api_key)])


class ClientSchema(BaseModel):
    id: int
    external_id: str
    email: str | None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ClientCreate(BaseModel):
    external_id: str
    email: str | None = None


@router.get("/", response_model=List[ClientSchema])
async def get_clients(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client))
    return result.scalars().all()


@router.post("/", response_model=ClientSchema)
async def create_client(client_data: ClientCreate, db: AsyncSession = Depends(get_db)):
    client = Client(**client_data.model_dump())
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


@router.get("/{client_id}", response_model=ClientSchema)
async def get_client(client_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.delete("/{client_id}")
async def delete_client(client_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    await db.delete(client)
    await db.commit()
    return {"status": "success"}
