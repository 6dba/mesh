import os
import subprocess

import typer
from rich.console import Console

app = typer.Typer(help="Deploy Kosatka components using Ansible")
console = Console()


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
