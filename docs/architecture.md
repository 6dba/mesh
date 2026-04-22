# KOSATKA Mesh Architecture

KOSATKA Mesh is a centralized control plane for managing distributed access nodes.

## Components

- **Master**: Centralized API and database. Manages nodes, subscriptions, and events.
- **Agent**: Lightweight process running on access nodes. Communicates with the Master and manages local providers.
- **Providers**: Specialized software for providing access (e.g., Marzban, AmneziaWG).
- **CLI**: Command-line tool for interacting with the Master.
- **SDK**: Python library for integrating KOSATKA into other applications.

## Data Flow

1. Master receives a request (e.g., create a subscription).
2. Master updates the database and schedules a sync task.
3. Master sends instructions to the relevant Agent(s) via webhooks or polling.
4. Agent executes instructions through its local Providers.
5. Agent reports back the status to the Master.
