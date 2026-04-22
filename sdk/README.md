# Kosatka Mesh SDK

Python SDK for interacting with the Kosatka Mesh Master API.

## Installation

```bash
pip install -e ./sdk
```

## Quick Start

```python
import asyncio
from kosatka_sdk.client import KosatkaClient

async def main():
    client = KosatkaClient(
        base_url="http://localhost:8000",
        api_key="your-api-key"
    )

    nodes = await client.list_nodes()
    for node in nodes:
        print(f"Node: {node.name} ({node.status})")

if __name__ == "__main__":
    asyncio.run(main())
```

## Key Components

- **KosatkaClient**: Main entry point for API interactions.
- **Models**: Pydantic models for type-safe data handling (`Node`, `Client`, `Subscription`).
- **Webhooks**: Utilities for verifying and parsing Kosatka webhooks.

## Examples

Check the `examples/` directory for common workflows:
- `basic_usage.py`: Node listing and health checks.
- `subscription_flow.py`: Client creation and subscription management.
- `multi_node.py`: Handling multiple nodes and status monitoring.
