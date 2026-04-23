import json
from unittest.mock import AsyncMock, patch

import pytest
import respx
from httpx import Response
from kosatka_agent.providers import _wgcore
from kosatka_agent.providers.marzban import MarzbanProvider
from kosatka_agent.providers.wireguard import WireGuardProvider


@pytest.mark.asyncio
async def test_marzban_provider_get_token():
    url = "http://marzban:8000"
    username = "admin"
    password = "password"
    provider = MarzbanProvider(url, username, password)

    with respx.mock:
        respx.post(f"{url}/api/admin/token").mock(
            return_value=Response(200, json={"access_token": "test-token"})
        )

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
async def test_wireguard_provider(tmp_path):
    # Stub out subprocess calls and the on-disk server-info file so this
    # unit test does not depend on `wg`/`awg` being installed on the host.
    server_info = tmp_path / "awg_server.json"
    server_info.write_text(
        json.dumps(
            {
                "public_key": "server-pub",
                "endpoint": "node.example.com:51820",
                "subnet": "10.8.0.0/24",
                "dns": "1.1.1.1",
            }
        )
    )
    state_path = tmp_path / "wg_peers.json"

    provider = WireGuardProvider("/etc/wireguard/wg0.conf")
    provider.server_info_path = str(server_info)
    provider.state_path = str(state_path)

    async def fake_run(cmd, stdin_text=None):
        head = cmd[:2]
        if head == ["wg", "genkey"]:
            return "client-priv"
        if head == ["wg", "pubkey"]:
            return "client-pub"
        if head == ["wg", "genpsk"]:
            return "client-psk"
        if cmd[:3] == ["wg", "show", provider.interface]:
            return "client-pub\tpsk\tendpoint\t10.8.0.2/32\t0\t0\t0\t0"
        # Everything else (set/save) is a no-op in tests.
        return ""

    with patch.object(_wgcore, "run", AsyncMock(side_effect=fake_run)):
        assert await provider.get_clients() == []
        assert await provider.get_client("1") is None

        res = await provider.create_client({"external_id": "client1"})
        assert res["id"] == "client1"
        assert "[Interface]" in res["config_text"]

        assert await provider.delete_client("client1") is True
        # After deletion the config fetch returns empty.
        assert await provider.get_client_config("client1") == ""
