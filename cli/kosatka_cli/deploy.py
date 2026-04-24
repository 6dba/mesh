import os
import subprocess

import typer
from rich.console import Console

from .config import load_config

app = typer.Typer(help="Deploy Kosatka components using Ansible")
console = Console()


@app.command("node")
def deploy_node(
    host: str = typer.Argument(..., help="Host to deploy to (e.g. root@1.2.3.4)"),
    identity_file: str = typer.Option(
        None, "--identity-file", "-i", help="Path to SSH private key"
    ),
    protocol: str = typer.Option("awg", help="VPN protocol to provision (awg, wireguard)"),
):
    """Deploy a single node via SSH using the remote installer"""
    config = load_config()
    master_url = config.base_url.rstrip("/")
    token = config.api_key

    if not token:
        console.print(
            "[bold red]Error: API Key not found in config. Please login first.[/bold red]"
        )
        raise typer.Exit(1)

    # Construct the remote command
    # We pass the token and protocol to the install script
    remote_cmd = (
        f"curl -sL {master_url}/static/install.sh | "
        f"bash -s -- --token {token} --protocol {protocol} --master-url {master_url}"
    )

    ssh_cmd = ["ssh", host, remote_cmd]
    if identity_file:
        ssh_cmd.insert(1, "-i")
        ssh_cmd.insert(2, identity_file)

    console.print(f"[bold blue]Deploying to {host}...[/bold blue]")
    console.print(f"[dim]Command: {' '.join(ssh_cmd)}[/dim]")

    try:
        # Use subprocess.run with check=True to stream output and handle errors
        subprocess.run(ssh_cmd, check=True)
        console.print(f"[bold green]Node {host} successfully deployed and registered![/bold green]")
    except subprocess.CalledProcessError as e:
        console.print(
            f"[bold red]Deployment to {host} failed with exit code {e.returncode}[/bold red]"
        )
    except FileNotFoundError:
        console.print("[bold red]Error: 'ssh' command not found.[/bold red]")


def run_ansible(extra_vars: str = None, tags: str = None):
    # This assumes we are running from the project root or have access to the ansible dir
    ansible_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../ansible"))
    inventory = os.path.join(ansible_dir, "inventory/hosts.yml")
    playbook = os.path.join(ansible_dir, "site.yml")

    if not os.path.exists(inventory):
        # Fallback to example if real one doesn't exist
        inventory = os.path.join(ansible_dir, "inventory/hosts.example.yml")

    cmd = ["ansible-playbook", "-i", inventory, playbook]
    if extra_vars:
        cmd.extend(["--extra-vars", extra_vars])
    if tags:
        cmd.extend(["--tags", tags])

    console.print(f"[bold blue]Running deployment:[/bold blue] {' '.join(cmd)}")
    try:
        # In a real scenario, we might want to capture output and stream it
        subprocess.run(cmd, check=True)
        console.print("[bold green]Deployment completed successfully![/bold green]")
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]Deployment failed with exit code {e.returncode}[/bold red]")
    except FileNotFoundError:
        console.print(
            "[bold red]Error: 'ansible-playbook' not found. Please install Ansible.[/bold red]"
        )


@app.command("all")
def deploy_all():
    """Deploy everything (Master + all Nodes)"""
    run_ansible()


@app.command("master")
def deploy_master():
    """Deploy only the Master node"""
    run_ansible(tags="master")


@app.command("nodes")
def deploy_nodes():
    """Deploy only the Agent nodes"""
    run_ansible(tags="agent")
