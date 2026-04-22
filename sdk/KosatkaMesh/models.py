from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class NodeBase(BaseModel):
    name: str
    address: str
    provider_type: str = "agent"


class NodeCreate(NodeBase):
    pass


class Node(NodeBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    last_seen: datetime
    is_active: bool
    metadata_json: Dict[str, Any]


class ClientBase(BaseModel):
    external_id: str
    email: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class Client(ClientBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime


class SubscriptionBase(BaseModel):
    client_id: int
    plan_name: str
    expires_at: datetime


class SubscriptionCreate(SubscriptionBase):
    pass


class Subscription(SubscriptionBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool


class WebhookEvent(BaseModel):
    event_type: str
    payload: Dict[str, Any]
    timestamp: datetime
