import pytest
import respx
from httpx import Response
from KosatkaMesh.client import MeshClient
from KosatkaMesh.models import NodeCreate


@pytest.fixture
def client():
    return MeshClient(base_url="http://api.test", api_key="test-key")


@respx.mock
@pytest.mark.asyncio
async def test_list_nodes(client):
    respx.get("http://api.test/api/v1/nodes").mock(
        return_value=Response(
            200,
            json=[
                {
                    "id": 1,
                    "name": "node1",
                    "address": "1.1.1.1",
                    "provider_type": "agent",
                    "status": "online",
                    "is_active": True,
                    "last_seen": "2023-01-01T00:00:00",
                    "metadata_json": {},
                }
            ],
        )
    )

    nodes = await client.list_nodes()
    assert len(nodes) == 1
    assert nodes[0].name == "node1"


@respx.mock
@pytest.mark.asyncio
async def test_register_node(client):
    respx.post("http://api.test/api/v1/nodes").mock(
        return_value=Response(
            200,
            json={
                "id": 2,
                "name": "new-node",
                "address": "2.2.2.2",
                "provider_type": "agent",
                "status": "online",
                "is_active": True,
                "last_seen": "2023-01-01T00:00:00",
                "metadata_json": {},
            },
        )
    )

    node_in = NodeCreate(name="new-node", address="2.2.2.2")
    node = await client.register_node(node_in)
    assert node.id == 2
    assert node.name == "new-node"


@respx.mock
@pytest.mark.asyncio
async def test_api_error(client):
    respx.get("http://api.test/api/v1/nodes").mock(
        return_value=Response(500, text="Internal Server Error")
    )

    from KosatkaMesh.exceptions import KosatkaAPIError

    with pytest.raises(KosatkaAPIError) as exc:
        await client.list_nodes()
    assert exc.value.status_code == 500
