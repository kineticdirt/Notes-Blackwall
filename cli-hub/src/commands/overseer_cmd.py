import click
from pathlib import Path
from rich.console import Console

console = Console()


@click.group("overseer")
def overseer():
    """Overseer monitoring and control."""
    pass


@overseer.command()
def status():
    """Show overseer status."""
    from ..dispatch import WORKSPACE_ROOT

    log_path = WORKSPACE_ROOT / ".overseer" / "overseer.log"
    if not log_path.exists():
        console.print("[yellow]No overseer log found.[/yellow]")
        return

    lines = log_path.read_text().strip().splitlines()
    console.print(f"[bold]Overseer log:[/bold] {len(lines)} entries")
    for line in lines[-10:]:
        console.print(f"  {line}")


@overseer.command()
def run():
    """Run the overseer."""
    from ..dispatch import dispatch
    dispatch(".", ["run_overseer.py"])
