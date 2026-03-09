import click
import subprocess
from rich.console import Console

console = Console()


@click.group("gateway")
def gateway():
    """API gateway management."""
    pass


@gateway.command()
@click.option("--port", default=9000)
def health(port):
    """Check gateway health."""
    try:
        import urllib.request
        resp = urllib.request.urlopen(f"http://localhost:{port}/health", timeout=5)
        data = resp.read().decode()
        console.print(f"[green]Gateway healthy:[/green] {data}")
    except Exception as e:
        console.print(f"[red]Gateway unreachable:[/red] {e}")


@gateway.command()
def start():
    """Start the API gateway."""
    from ..dispatch import dispatch
    dispatch("api-gateway", ["-m", "src"])
