import click
from rich.console import Console

console = Console()


@click.group("infra")
def infra():
    """Infrastructure deployment helpers."""
    pass


@infra.command()
def up():
    """Start local dev environment via Docker Compose."""
    from ..dispatch import dispatch
    import subprocess, sys
    from ..dispatch import WORKSPACE_ROOT

    compose_file = WORKSPACE_ROOT / "infrastructure-blueprints" / "docker" / "docker-compose.yml"
    if not compose_file.exists():
        console.print("[red]docker-compose.yml not found[/red]")
        return

    console.print("[bold]Starting local dev environment...[/bold]")
    subprocess.run(["docker", "compose", "-f", str(compose_file), "up", "-d"])


@infra.command()
def down():
    """Stop local dev environment."""
    from ..dispatch import WORKSPACE_ROOT
    import subprocess

    compose_file = WORKSPACE_ROOT / "infrastructure-blueprints" / "docker" / "docker-compose.yml"
    subprocess.run(["docker", "compose", "-f", str(compose_file), "down"])


@infra.command()
def status():
    """Show running containers."""
    import subprocess
    subprocess.run(["docker", "compose", "ps"])
