from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException
from kosatka_master.config import settings
from kosatka_master.database import get_db
from kosatka_master.models.client import Client
from kosatka_master.models.node import Node
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


class ClientProvisionRequest(BaseModel):
    """Create-or-get a client and materialize a VPN peer on an agent node."""

    external_id: str
    email: Optional[str] = None
    # Which provider family to provision on. Must match Node.provider_type
    # of the agent that will answer (awg | wireguard | marzban | xray).
    protocol: str = "awg"
    # Optional pin to a specific node; otherwise master picks any active
    # node matching `protocol`.
    node_id: Optional[int] = None


class ClientProvisionResponse(BaseModel):
    id: int
    external_id: str
    node_id: int
    provider_type: str
    config_text: str
    address: Optional[str] = None
    public_key: Optional[str] = None


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


async def _pick_node(db: AsyncSession, protocol: str, node_id: Optional[int]) -> Node:
    if node_id is not None:
        q = await db.execute(select(Node).where(Node.id == node_id))
        node = q.scalar_one_or_none()
        if node is None:
            raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
        return node

    q = await db.execute(
        select(Node).where(Node.is_active.is_(True), Node.provider_type == protocol).limit(1)
    )
    node = q.scalar_one_or_none()
    if node is None:
        raise HTTPException(
            status_code=503,
            detail=f"No active nodes available for provider_type={protocol!r}",
        )
    return node


async def _call_agent(node: Node, method: str, path: str, **kwargs: Any) -> Dict[str, Any]:
    url = f"{node.address.rstrip('/')}{path}"
    headers = {"X-Kosatka-Key": settings.api_key}
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.request(method, url, headers=headers, **kwargs)
    if resp.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=f"Agent {node.name} returned {resp.status_code}: {resp.text[:256]}",
        )
    return resp.json()


@router.post("/provision", response_model=ClientProvisionResponse)
async def provision_client(
    req: ClientProvisionRequest, db: AsyncSession = Depends(get_db)
) -> ClientProvisionResponse:
    """Create-or-get a Client row, pick a node, and ask the agent to
    materialize the peer. Returns the ready-to-import client config."""
    # Idempotent create of the client record.
    existing = await db.execute(select(Client).where(Client.external_id == req.external_id))
    client = existing.scalar_one_or_none()
    if client is None:
        client = Client(external_id=req.external_id, email=req.email)
        db.add(client)
        await db.commit()
        await db.refresh(client)
    elif req.email and client.email != req.email:
        client.email = req.email
        await db.commit()
        await db.refresh(client)

    node = await _pick_node(db, req.protocol, req.node_id)

    agent_payload = {"external_id": req.external_id, "email": req.email}
    agent_result = await _call_agent(node, "POST", "/clients", json=agent_payload)

    config_text = agent_result.get("config_text") or ""
    if not config_text:
        # Fall back to a dedicated config fetch if the agent returned a bare result.
        try:
            follow_up = await _call_agent(node, "GET", f"/clients/{req.external_id}/config")
            config_text = follow_up.get("config", "") or ""
        except HTTPException:
            config_text = ""

    return ClientProvisionResponse(
        id=client.id,
        external_id=client.external_id,
        node_id=node.id,
        provider_type=node.provider_type,
        config_text=config_text,
        address=agent_result.get("address"),
        public_key=agent_result.get("public_key"),
    )


@router.get("/by-external/{external_id}/config")
async def get_client_config_by_external(
    external_id: str, node_id: Optional[int] = None, db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Proxy to the agent's `/clients/{external_id}/config`."""
    if node_id is not None:
        q = await db.execute(select(Node).where(Node.id == node_id))
    else:
        q = await db.execute(select(Node).where(Node.is_active.is_(True)).limit(1))
    node = q.scalar_one_or_none()
    if node is None:
        raise HTTPException(status_code=404, detail="No node available")
    return await _call_agent(node, "GET", f"/clients/{external_id}/config")
