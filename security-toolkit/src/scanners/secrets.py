import math
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Finding:
    file: str
    line: int
    rule: str
    match: str
    severity: str = "high"


PATTERNS: list[tuple[str, re.Pattern]] = [
    ("AWS Access Key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("AWS Secret Key", re.compile(r"(?i)aws_secret_access_key\s*[=:]\s*['\"]?([A-Za-z0-9/+=]{40})")),
    ("Generic API Key", re.compile(r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"]?([A-Za-z0-9_\-]{20,})")),
    ("Generic Secret", re.compile(r"(?i)(secret|password|passwd|token)\s*[=:]\s*['\"]?([^\s'\"]{8,})")),
    ("Private Key", re.compile(r"-----BEGIN (RSA |EC |DSA )?PRIVATE KEY-----")),
    ("GitHub Token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,}")),
    ("Anthropic Key", re.compile(r"sk-ant-api\d{2}-[A-Za-z0-9_\-]{80,}")),
    ("Slack Token", re.compile(r"xox[baprs]-[0-9]{10,}-[A-Za-z0-9]+")),
    ("JWT", re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]+")),
]

SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", ".mypy_cache"}
SKIP_EXTENSIONS = {".pyc", ".pyo", ".so", ".dylib", ".png", ".jpg", ".gif", ".ico", ".woff", ".ttf"}


def shannon_entropy(data: str) -> float:
    if not data:
        return 0.0
    freq: dict[str, int] = {}
    for c in data:
        freq[c] = freq.get(c, 0) + 1
    length = len(data)
    return -sum((count / length) * math.log2(count / length) for count in freq.values())


def scan_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        text = path.read_text(errors="replace")
    except (PermissionError, OSError):
        return findings

    for line_num, line in enumerate(text.splitlines(), start=1):
        for rule_name, pattern in PATTERNS:
            if pattern.search(line):
                findings.append(Finding(
                    file=str(path),
                    line=line_num,
                    rule=rule_name,
                    match=line.strip()[:120],
                ))
    return findings


def scan_directory(root: Path, skip_dirs: set[str] | None = None) -> list[Finding]:
    skip = skip_dirs or SKIP_DIRS
    findings: list[Finding] = []
    for path in root.rglob("*"):
        if any(part in skip for part in path.parts):
            continue
        if path.is_file() and path.suffix not in SKIP_EXTENSIONS:
            findings.extend(scan_file(path))
    return findings
