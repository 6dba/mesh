import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
from kosatka_master.services.node_manager import NodeManager
from kosatka_master.services.subscription_engine import SubscriptionEngine
from kosatka_master.models.node import Node
from kosatka_master.models.subscription import Subscription

@pytest.mark.asyncio
async def test_node_manager_register_node():
    db = AsyncMock()
    manager = NodeManager(db)
    
    node = await manager.register_node("Test Node", "1.2.3.4", "agent")
    
    assert node.name == "Test Node"
    assert node.address == "1.2.3.4"
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()

@pytest.mark.asyncio
async def test_node_manager_sync_all_nodes():
    db = AsyncMock()
    
    # Mock result for select(Node)
    mock_node = Node(id=1, name="Node 1", address="1.1.1.1", is_active=True)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_node]
    db.execute.return_value = mock_result
    
    manager = NodeManager(db)
    
    # Patch the class in the module where it's used
    with patch("kosatka_master.services.node_manager.AgentNodeProvider") as mock_provider_cls:
        mock_provider = MagicMock()
        mock_provider.sync_node = AsyncMock(return_value=True)
        mock_provider_cls.return_value = mock_provider
        
        await manager.sync_all_nodes()
        
        assert mock_node.status == "online"
        assert mock_node.last_seen is not None
        db.commit.assert_called_once()
        mock_provider.sync_node.assert_called_with("1.1.1.1")

@pytest.mark.asyncio
async def test_subscription_engine_create():
    db = AsyncMock()
    engine = SubscriptionEngine(db)
    
    expiry = datetime.utcnow() + timedelta(days=30)
    sub = await engine.create_subscription(1, "Premium", expiry)
    
    assert sub.client_id == 1
    assert sub.plan_name == "Premium"
    assert sub.expires_at == expiry
    db.add.assert_called_once()
    db.commit.assert_called_once()

@pytest.mark.asyncio
async def test_subscription_engine_check_expirations():
    db = AsyncMock()
    engine = SubscriptionEngine(db)
    
    await engine.check_expirations()
    
    db.execute.assert_called_once()
    db.commit.assert_called_once()
