#!/bin/bash
set -e

INVENTORY=${1:-inventory/hosts.example.yml}
shift || true

echo "Deploying KOSATKA Mesh using inventory: $INVENTORY"
ansible-playbook -i "$INVENTORY" site.yml "$@"
