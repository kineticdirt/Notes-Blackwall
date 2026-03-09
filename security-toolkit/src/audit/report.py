import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from ..scanners.secrets import Finding
from ..scanners.dependencies import VulnFinding


def generate_json_report(
    secret_findings: list[Finding],
    vuln_findings: list[VulnFinding],
    output: Path,
):
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "secrets": len(secret_findings),
            "vulnerabilities": len(vuln_findings),
            "total": len(secret_findings) + len(vuln_findings),
        },
        "secrets": [asdict(f) for f in secret_findings],
        "vulnerabilities": [asdict(f) for f in vuln_findings],
    }
    output.write_text(json.dumps(report, indent=2))
    return report


def generate_markdown_report(
    secret_findings: list[Finding],
    vuln_findings: list[VulnFinding],
    output: Path,
):
    lines = [
        "# Security Scan Report",
        f"\n**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"\n## Summary\n",
        f"| Category | Count |",
        f"|----------|-------|",
        f"| Secrets  | {len(secret_findings)} |",
        f"| Vulnerabilities | {len(vuln_findings)} |",
        f"| **Total** | **{len(secret_findings) + len(vuln_findings)}** |",
    ]

    if secret_findings:
        lines.append("\n## Secrets Found\n")
        lines.append("| File | Line | Rule | Severity |")
        lines.append("|------|------|------|----------|")
        for f in secret_findings:
            lines.append(f"| `{f.file}` | {f.line} | {f.rule} | {f.severity} |")

    if vuln_findings:
        lines.append("\n## Vulnerabilities\n")
        lines.append("| Package | Version | ID | Severity | Fix |")
        lines.append("|---------|---------|-----|----------|-----|")
        for v in vuln_findings:
            fix = v.fix_version or "—"
            lines.append(f"| {v.package} | {v.installed_version} | {v.vulnerability_id} | {v.severity} | {fix} |")

    output.write_text("\n".join(lines))
