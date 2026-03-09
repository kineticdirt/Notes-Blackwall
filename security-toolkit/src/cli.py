import click
from pathlib import Path
from rich.console import Console
from rich.table import Table

from .scanners.secrets import scan_directory, Finding
from .scanners.dependencies import scan_workspace, VulnFinding
from .audit.report import generate_json_report, generate_markdown_report

console = Console()


@click.group()
def cli():
    """Cequence BlackWall Security Toolkit"""
    pass


@cli.command()
@click.option("--secrets/--no-secrets", default=True, help="Run secrets scan")
@click.option("--deps/--no-deps", default=True, help="Run dependency audit")
@click.option("--all", "run_all", is_flag=True, help="Run all scanners")
@click.option("--path", default=".", help="Root directory to scan")
def scan(secrets: bool, deps: bool, run_all: bool, path: str):
    """Run security scans on the workspace."""
    root = Path(path).resolve()
    secret_findings: list[Finding] = []
    vuln_findings: list[VulnFinding] = []

    if run_all or secrets:
        console.print("[bold]Scanning for secrets...[/bold]")
        secret_findings = scan_directory(root)
        if secret_findings:
            table = Table(title="Secrets Found")
            table.add_column("File")
            table.add_column("Line")
            table.add_column("Rule")
            table.add_column("Severity")
            for f in secret_findings:
                table.add_row(f.file, str(f.line), f.rule, f.severity)
            console.print(table)
        else:
            console.print("[green]No secrets found.[/green]")

    if run_all or deps:
        console.print("[bold]Auditing dependencies...[/bold]")
        vuln_findings = scan_workspace(root)
        if vuln_findings:
            table = Table(title="Vulnerabilities")
            table.add_column("Package")
            table.add_column("Version")
            table.add_column("ID")
            table.add_column("Severity")
            for v in vuln_findings:
                table.add_row(v.package, v.installed_version, v.vulnerability_id, v.severity)
            console.print(table)
        else:
            console.print("[green]No known vulnerabilities.[/green]")

    total = len(secret_findings) + len(vuln_findings)
    console.print(f"\n[bold]Total findings: {total}[/bold]")


@cli.command()
@click.option("--format", "fmt", type=click.Choice(["json", "markdown"]), default="markdown")
@click.option("--output", default="security-report", help="Output filename (without extension)")
@click.option("--path", default=".", help="Root directory to scan")
def report(fmt: str, output: str, path: str):
    """Generate a security report."""
    root = Path(path).resolve()
    console.print("[bold]Running full scan for report...[/bold]")

    secret_findings = scan_directory(root)
    vuln_findings = scan_workspace(root)

    if fmt == "json":
        out_path = Path(f"{output}.json")
        generate_json_report(secret_findings, vuln_findings, out_path)
    else:
        out_path = Path(f"{output}.md")
        generate_markdown_report(secret_findings, vuln_findings, out_path)

    console.print(f"[green]Report written to {out_path}[/green]")


@cli.command()
def version():
    """Show version."""
    console.print("security-toolkit v0.1.0")


def main():
    cli()


if __name__ == "__main__":
    main()
