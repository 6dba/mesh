import json
from unittest.mock import AsyncMock, patch

import pytest
from kosatka_agent.providers import _wgcore
from kosatka_agent.providers.awg import AmneziaWGProvider


@pytest.mark.asyncio
async def test_awg_provider(tmp_path):
    server_info = tmp_path / "awg_server.json"
    server_info.write_text(
        json.dumps(
            {
                "public_key": "server-pub",
                "endpoint": "node.example.com:51820",
                "subnet": "10.8.0.0/24",
                "dns": "1.1.1.1",
                "Jc": 4,
            }
        )
    )
    state_path = tmp_path / "awg_peers.json"

    provider = AmneziaWGProvider("/etc/amnezia/amneziawg/wg0.conf")
    provider.server_info_path = str(server_info)
    provider.state_path = str(state_path)

    async def fake_run(cmd, stdin_text=None):
        head = cmd[:2]
        if head == ["awg", "genkey"]:
            return "client-priv"
        if head == ["awg", "pubkey"]:
            return "client-pub"
        if head == ["awg", "genpsk"]:
            return "client-psk"
        if cmd[:3] == ["awg", "show", provider.interface]:
            return "client-pub\tpsk\tendpoint\t10.8.0.2/32\t0\t100\t200\t0"
        return ""

    with patch.object(_wgcore, "run", AsyncMock(side_effect=fake_run)):
        # Test initial state
        assert await provider.get_clients() == []

        # Test create client
        res = await provider.create_client({"external_id": "user1"})
        assert res["id"] == "user1"
        assert res["public_key"] == "client-pub"
        assert "Jc = 4" in res["config_text"]

        # Test idempotency
        res2 = await provider.create_client({"external_id": "user1"})
        assert res2["id"] == "user1"

        # Test get_client
        client = await provider.get_client("user1")
        assert client["client_id"] == "user1"

        # Test get_clients
        clients = await provider.get_clients()
        assert len(clients) == 1

        # Test stats
        stats = await provider.get_client_stats("user1")
        assert stats["transfer_rx"] == 100
        assert stats["transfer_tx"] == 200

        # Test delete
        assert await provider.delete_client("user1") is True
        assert await provider.get_client("user1") is None
        assert await provider.delete_client("user1") is False


@pytest.mark.asyncio
async def test_awg_provider_no_server_info(tmp_path):
    provider = AmneziaWGProvider()
    provider.server_info_path = str(tmp_path / "missing.json")
    with pytest.raises(RuntimeError):
        await provider.create_client({"id": "1"})
