import pytest
from kosatka_master.config import settings

@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_get_nodes_unauthorized(client):
    response = await client.get("/api/v1/nodes/")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_and_get_node(client):
    headers = {"X-Kosatka-Key": settings.api_key}
    
    # Create node
    node_data = {
        "name": "test-node",
        "address": "1.2.3.4",
        "provider_type": "agent"
    }
    response = await client.post("/api/v1/nodes/", json=node_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-node"
    node_id = data["id"]
    
    # Get nodes
    response = await client.get("/api/v1/nodes/", headers=headers)
    assert response.status_code == 200
    nodes = response.json()
    assert len(nodes) >= 1
    assert any(n["id"] == node_id for n in nodes)

@pytest.mark.asyncio
async def test_delete_node(client):
    headers = {"X-Kosatka-Key": settings.api_key}
    
    # Create
    node_data = {"name": "to-delete", "address": "1.1.1.1"}
    response = await client.post("/api/v1/nodes/", json=node_data, headers=headers)
    node_id = response.json()["id"]
    
    # Delete
    response = await client.delete(f"/api/v1/nodes/{node_id}", headers=headers)
    assert response.status_code == 200
    
    # Verify deleted
    response = await client.get("/api/v1/nodes/", headers=headers)
    nodes = response.json()
    assert all(n["id"] != node_id for n in nodes)
