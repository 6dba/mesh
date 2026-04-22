import asyncio
import os
from KosatkaMesh.client import MeshClient

async def main():
    base_url = os.getenv("KOSATKA_BASE_URL", "http://localhost:8000")
    api_key = os.getenv("KOSATKA_API_KEY", "your-secret-key")

    client = MeshClient(base_url=base_url, api_key=api_key)

    print("--- Multi-Node Status ---")
    try:
        nodes = await client.list_nodes()
        
        if not nodes:
            print("No nodes registered.")
            return

        online_nodes = [n for n in nodes if n.status == "online"]
        offline_nodes = [n for n in nodes if n.status != "online"]

        print(f"Total Nodes: {len(nodes)}")
        print(f"Online: {len(online_nodes)}")
        print(f"Offline: {len(offline_nodes)}")

        for node in online_nodes:
            print(f"\nNode: {node.name} ({node.address})")
            health = await client.get_node_health(node.id)
            load = health.get("load", "N/A")
            print(f"  System Load: {load}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
