# Adding a New Provider

To add a new provider to KOSATKA Agent:

1. Create a new provider class in `agent/kosatka_agent/providers/`.
2. Inherit from the `BaseProvider` class.
3. Implement the required methods: `sync()`, `get_status()`, etc.
4. Register the provider in the agent's configuration.

Example:
```python
from .base import BaseProvider

class MyNewProvider(BaseProvider):
    async def sync(self, data):
        # Implementation logic
        pass
```
