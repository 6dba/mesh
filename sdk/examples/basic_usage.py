import asyncio
import os

from KosatkaMesh.client import MeshClient
from KosatkaMesh.models import NodeCreate


async def main():
    # Use environment variables for configuration
    base_url = os.getenv("KOSATKA_BASE_URL", "http://localhost:8000")
    api_key = os.getenv("KOSATKA_API_KEY", "your-secret-key")

    client = MeshClient(base_url=base_url, api_key=api_key)

    print("--- Listing Nodes ---")
    try:
        nodes = await client.list_nodes()
        if not nodes:
            print("No nodes found. Registering a test node...")
            new_node = await client.register_node(
                NodeCreate(name="example-node", address="127.0.0.1", provider_type="agent")
            )
            print(f"Registered node: {new_node.name} (ID: {new_node.id})")
            nodes = [new_node]

        for node in nodes:
            print(f"Node: {node.name} | Status: {node.status} | Address: {node.address}")
            health = await client.get_node_health(node.id)
            print(f"  Health: {health}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
