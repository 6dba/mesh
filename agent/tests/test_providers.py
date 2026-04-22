import pytest
import respx
from httpx import Response
from kosatka_agent.providers.marzban import MarzbanProvider
from kosatka_agent.providers.wireguard import WireGuardProvider

@pytest.mark.asyncio
async def test_marzban_provider_get_token():
    url = "http://marzban:8000"
    username = "admin"
    password = "password"
    provider = MarzbanProvider(url, username, password)

    with respx.mock:
        respx.post(f"{url}/api/admin/token").mock(return_value=Response(200, json={"access_token": "test-token"}))
        
        token = await provider._get_token()
        assert token == "test-token"
        assert provider.token == "test-token"
        
        # Second call should use cached token
        token2 = await provider._get_token()
        assert token2 == "test-token"

@pytest.mark.asyncio
async def test_marzban_provider_methods():
    provider = MarzbanProvider("http://marzban", "admin", "pass")
    
    assert await provider.get_clients() == []
    assert await provider.get_client("1") is None
    
    client_data = {"username": "user1"}
    res = await provider.create_client(client_data)
    assert res["id"] == "user1"
    
    assert await provider.delete_client("user1") is True
    assert "vless://" in await provider.get_client_config("user1")
    assert (await provider.get_client_stats("user1"))["usage"] == 0

@pytest.mark.asyncio
async def test_wireguard_provider():
    provider = WireGuardProvider("/etc/wireguard/wg0.conf")
    
    assert await provider.get_clients() == []
    assert await provider.get_client("1") is None
    
    client_data = {"external_id": "client1"}
    res = await provider.create_client(client_data)
    assert res["id"] == "client1"
    
    assert await provider.delete_client("client1") is True
    assert "[Interface]" in await provider.get_client_config("client1")
    assert (await provider.get_client_stats("client1"))["transfer_rx"] == 0
