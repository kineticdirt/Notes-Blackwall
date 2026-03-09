"""
Sacrificial low-parameter prompt injection detection and remedy.

User input is first passed through a sacrificial detector (rule-based + optional
small model). If injection is detected, input is sanitized or blocked before
reaching the main AI.
"""

from .detector import SacrificialDetector, ScanResult
from .gate import GateResult, SacrificialGate
from .remedy import RemedyResult, sanitize

__all__ = [
    "SacrificialDetector",
    "ScanResult",
    "SacrificialGate",
    "GateResult",
    "RemedyResult",
    "sanitize",
]
