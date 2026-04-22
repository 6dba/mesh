# Quickstart Guide

## 1. Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv)
- Docker and Docker Compose (optional)

## 2. Installation
```bash
git clone https://github.com/your-repo/kosatka-mesh.git
cd kosatka-mesh
uv pip install -e .
```

## 3. Running Services
```bash
# Start Master
kosatka-mesh master run

# In another terminal, start Agent
kosatka-mesh agent run
```

## 4. Local Development with Docker
```bash
make dev-up
```

## 5. Production Deployment
Check the [Deployment Guide](cli.md#deployment) for using Ansible:
```bash
cd ansible
cp inventory/hosts.example.yml inventory/hosts.yml
# Edit inventory/hosts.yml
./deploy.sh inventory/hosts.yml
```

## 6. Using the CLI
```bash
kosatka-mesh login http://localhost:8000 your-api-key
kosatka-mesh nodes list
```
