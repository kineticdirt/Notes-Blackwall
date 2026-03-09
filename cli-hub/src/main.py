import click
from rich.console import Console

from .commands.blackwall_cmd import blackwall
from .commands.security_cmd import security
from .commands.pipeline_cmd import pipeline
from .commands.gateway_cmd import gateway
from .commands.overseer_cmd import overseer
from .commands.infra_cmd import infra

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="cq")
def cli():
    """cq — Cequence BlackWall unified CLI.

    One entry point for all workspace tools: protection, security,
    pipelines, infrastructure, and monitoring.
    """
    pass


cli.add_command(blackwall)
cli.add_command(security)
cli.add_command(pipeline)
cli.add_command(gateway)
cli.add_command(overseer)
cli.add_command(infra)


@cli.command()
def status():
    """Show status of all services."""
    import urllib.request

    services = [
        ("BlackWall", "http://localhost:8000/health"),
        ("API Gateway", "http://localhost:9000/health"),
        ("Workflow Canvas", "http://localhost:8080/health"),
    ]
    for name, url in services:
        try:
            resp = urllib.request.urlopen(url, timeout=3)
            console.print(f"  [green]●[/green] {name}: up")
        except Exception:
            console.print(f"  [red]●[/red] {name}: down")


if __name__ == "__main__":
    cli()
