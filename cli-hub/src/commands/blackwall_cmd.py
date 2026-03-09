import click
from ..dispatch import dispatch


@click.group("blackwall")
def blackwall():
    """BlackWall AI protection tools."""
    pass


@blackwall.command()
@click.argument("args", nargs=-1)
def protect(args):
    """Run BlackWall protection."""
    dispatch("blackwall", ["-m", "blackwall.cli", "protect", *args])


@blackwall.command()
@click.argument("args", nargs=-1)
def detect(args):
    """Run BlackWall detection."""
    dispatch("blackwall", ["-m", "blackwall.cli", "detect", *args])
