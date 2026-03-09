import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class VulnFinding:
    package: str
    installed_version: str
    vulnerability_id: str
    description: str
    fix_version: str | None
    severity: str


def audit_python(requirements_path: Path) -> list[VulnFinding]:
    """Run pip-audit against a requirements file."""
    findings: list[VulnFinding] = []
    try:
        result = subprocess.run(
            ["pip-audit", "-r", str(requirements_path), "--format", "json", "--output", "-"],
            capture_output=True, text=True, timeout=120,
        )
    except FileNotFoundError:
        return findings

    if result.stdout:
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            return findings
        for dep in data.get("dependencies", []):
            for vuln in dep.get("vulns", []):
                findings.append(VulnFinding(
                    package=dep["name"],
                    installed_version=dep["version"],
                    vulnerability_id=vuln.get("id", "unknown"),
                    description=vuln.get("description", ""),
                    fix_version=vuln.get("fix_versions", [None])[0] if vuln.get("fix_versions") else None,
                    severity=vuln.get("aliases", ["unknown"])[0] if vuln.get("aliases") else "unknown",
                ))
    return findings


def audit_node(package_dir: Path) -> list[VulnFinding]:
    """Run npm audit in a directory with package.json."""
    findings: list[VulnFinding] = []
    try:
        result = subprocess.run(
            ["npm", "audit", "--json"],
            capture_output=True, text=True, timeout=120, cwd=str(package_dir),
        )
    except FileNotFoundError:
        return findings

    if result.stdout:
        try:
            data = json.loads(result.stdout)
        except json.JSONDecodeError:
            return findings
        for name, advisory in data.get("vulnerabilities", {}).items():
            findings.append(VulnFinding(
                package=name,
                installed_version=advisory.get("range", "unknown"),
                vulnerability_id=str(advisory.get("via", [""])[0]) if advisory.get("via") else "",
                description=advisory.get("title", ""),
                fix_version=advisory.get("fixAvailable", {}).get("version") if isinstance(advisory.get("fixAvailable"), dict) else None,
                severity=advisory.get("severity", "unknown"),
            ))
    return findings


def scan_workspace(root: Path) -> list[VulnFinding]:
    findings: list[VulnFinding] = []
    for req in root.rglob("requirements.txt"):
        findings.extend(audit_python(req))
    for pkg in root.rglob("package.json"):
        if "node_modules" not in str(pkg):
            findings.extend(audit_node(pkg.parent))
    return findings
