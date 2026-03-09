# Security Toolkit

Traditional security tooling for Cequence BlackWall. Complements BlackWall's AI-specific protection with infrastructure and application security scanning.

## Capabilities

| Category | Tools | Purpose |
|----------|-------|---------|
| **Secrets detection** | Built-in scanner | Find leaked API keys, tokens, passwords in code and config |
| **Dependency audit** | pip-audit, npm audit | Known CVEs in Python/Node dependencies |
| **Container scanning** | Trivy integration | Vulnerabilities in Docker images |
| **SAST** | Bandit (Python), Semgrep | Static analysis for security bugs |
| **Policy enforcement** | OPA/Rego policies | Enforce org standards (no root containers, required labels, etc.) |
| **Network audit** | Port scanner | Check exposed services and open ports |

## Quick Start

```bash
pip install -r requirements.txt

# Run all scans on the workspace
python -m src.cli scan --all

# Secrets only
python -m src.cli scan --secrets

# Dependency audit
python -m src.cli scan --deps

# Generate report
python -m src.cli report --format html --output report.html
```

## Structure

```
security-toolkit/
├── src/
│   ├── scanners/          # Individual scanner implementations
│   │   ├── secrets.py     # Regex + entropy-based secret detection
│   │   ├── dependencies.py # pip-audit / npm audit wrapper
│   │   ├── containers.py  # Trivy wrapper for image scanning
│   │   └── sast.py        # Bandit / Semgrep integration
│   ├── audit/
│   │   ├── report.py      # Report generation (JSON, HTML, Markdown)
│   │   └── baseline.py    # Known-issue baseline management
│   └── cli.py             # CLI entry point
├── policies/              # OPA/Rego policy files
└── tests/
```

## Integration

- **Pre-commit hook**: Add secrets scanner to git pre-commit
- **CI pipeline**: Run full scan in GitHub Actions / GitLab CI
- **API Gateway**: Feed findings into observability-stack alerts
