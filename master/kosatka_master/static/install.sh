#!/bin/bash
set -e

# Kosatka Mesh — Universal Node Installer
# Usage: curl -sL http://master/static/install.sh | bash -s -- --token <KEY> --protocol <awg|wireguard>

show_help() {
    echo "Usage: install.sh --token <TOKEN> [--protocol <PROTOCOL>] [--master-url <URL>]"
    echo ""
    echo "Options:"
    echo "  --token       API Key for registering the node with Master"
    echo "  --protocol    VPN protocol to provision (default: awg)"
    echo "  --master-url  URL of the Kosatka Master (inferred if not provided)"
}

TOKEN=""
PROTOCOL="awg"
MASTER_URL=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --token) TOKEN="$2"; shift 2 ;;
        --protocol) PROTOCOL="$2"; shift 2 ;;
        --master-url) MASTER_URL="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; show_help; exit 1 ;;
    esac
done

if [ -z "$TOKEN" ]; then
    echo "Error: --token is required."
    show_help
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    OS=$(uname -s | tr '[:upper:]' '[:lower:]')
fi

echo "--- Detected OS: $OS ---"

# Install Dependencies
echo "--- Installing Python and Dependencies ---"
case $OS in
    ubuntu|debian)
        apt-get update
        apt-get install -y python3 python3-pip python3-venv curl tar gzip
        ;;
    centos|rhel|almalinux|rocky)
        yum install -y python3 python3-pip curl tar gzip
        ;;
    *)
        echo "Unsupported OS: $OS. Please install Python 3 and Ansible manually."
        exit 1
        ;;
esac

# Setup Ansible in VENV
echo "--- Setting up Ansible ---"
mkdir -p /opt/kosatka/bootstrap
cd /opt/kosatka/bootstrap
python3 -m venv venv
./venv/bin/pip install --upgrade pip
./venv/bin/pip install ansible-core

# Download Playbooks
if [ -z "$MASTER_URL" ]; then
    # SSH_CONNECTION is populated only when bash was launched inside an
    # SSH session, which is what `kosatka deploy node` uses. If the
    # operator runs the documented `curl … | bash` flow directly on the
    # host, SSH_CONNECTION is empty and the inferred URL becomes
    # `http://:8000`, which silently breaks the tarball download below.
    # Require an explicit --master-url in that case.
    if [ -n "$SSH_CONNECTION" ]; then
        MASTER_URL="http://${SSH_CONNECTION%% *}:8000"
        echo "--- Inferred Master URL: $MASTER_URL (verify if deployment fails) ---"
    else
        echo "Error: --master-url is required when not running over SSH."
        show_help
        exit 1
    fi
fi

echo "--- Downloading Playbooks from $MASTER_URL ---"
curl -sL "${MASTER_URL}/api/v1/static/ansible.tar.gz" -o ansible.tar.gz
tar -xzf ansible.tar.gz

# Run Ansible
echo "--- Running Deployment ---"
./venv/bin/ansible-playbook -i localhost, -c local site.yml \
    -e "kosatka_api_key=$TOKEN" \
    -e "kosatka_provider_type=$PROTOCOL" \
    -e "kosatka_master_url=$MASTER_URL"

echo "--- Node Deployment Successful! ---"
