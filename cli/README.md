# Kosatka Mesh CLI

The command-line interface for managing the Kosatka Mesh network.

## Installation

```bash
pip install -e ./cli
```

## Quick Start

1. **Log in** to your master instance:
   ```bash
   kosatka login <your-api-key> --base-url http://master-ip:8000
   ```

2. **List nodes**:
   ```bash
   kosatka nodes list
   ```

3. **Deploy** to all nodes:
   ```bash
   kosatka deploy all
   ```

4. **Run diagnostics**:
   ```bash
   kosatka doctor
   ```

## Commands

- `nodes`: Manage registered nodes (list, register, health).
- `deploy`: Ansible-based deployment of master and agents.
- `login`: Configure API access.
- `info`: Show current configuration.
- `doctor`: Run health checks.
