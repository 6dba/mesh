import pytest
from httpx import AsyncClient, ASGITransport
from kosatka_agent.main import app
from kosatka_agent.config import settings
from unittest.mock import AsyncMock, patch

@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

@pytest.mark.asyncio
async def test_unauthorized(client):
    response = await client.get("/clients")
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_get_clients(client):
    headers = {"X-Kosatka-Key": settings.api_key}
    
    with patch("kosatka_agent.main.provider") as mock_provider:
        mock_provider.get_clients = AsyncMock(return_value=[{"id": "test"}])
        
        response = await client.get("/clients", headers=headers)
        assert response.status_code == 200
        assert response.json() == [{"id": "test"}]

@pytest.mark.asyncio
async def test_create_client(client):
    headers = {"X-Kosatka-Key": settings.api_key}
    
    with patch("kosatka_agent.main.provider") as mock_provider:
        mock_provider.create_client = AsyncMock(return_value={"id": "new", "name": "test"})
        
        response = await client.post("/clients", json={"name": "test"}, headers=headers)
        assert response.status_code == 200
        assert response.json()["id"] == "new"

@pytest.mark.asyncio
async def test_delete_client_success(client):
    headers = {"X-Kosatka-Key": settings.api_key}
    
    with patch("kosatka_agent.main.provider") as mock_provider:
        mock_provider.delete_client = AsyncMock(return_value=True)
        
        response = await client.delete("/clients/test", headers=headers)
        assert response.status_code == 200
        assert response.json() == {"status": "deleted"}

@pytest.mark.asyncio
async def test_delete_client_not_found(client):
    headers = {"X-Kosatka-Key": settings.api_key}
    
    with patch("kosatka_agent.main.provider") as mock_provider:
        mock_provider.delete_client = AsyncMock(return_value=False)
        
        response = await client.delete("/clients/none", headers=headers)
        assert response.status_code == 404
