import click
from ..dispatch import dispatch


@click.group("security")
def security():
    """Security scanning and auditing."""
    pass


@security.command()
@click.option("--secrets/--no-secrets", default=True)
@click.option("--deps/--no-deps", default=True)
@click.option("--all", "run_all", is_flag=True)
@click.option("--path", default=".")
def scan(secrets, deps, run_all, path):
    """Run security scans."""
    args = ["-m", "src", "scan"]
    if run_all:
        args.append("--all")
    if not secrets:
        args.append("--no-secrets")
    if not deps:
        args.append("--no-deps")
    args.extend(["--path", path])
    dispatch("security-toolkit", args)


@security.command()
@click.option("--format", "fmt", type=click.Choice(["json", "markdown"]), default="markdown")
@click.option("--output", default="security-report")
def report(fmt, output):
    """Generate security report."""
    dispatch("security-toolkit", ["-m", "src", "report", "--format", fmt, "--output", output])
