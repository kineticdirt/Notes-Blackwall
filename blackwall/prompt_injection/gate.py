"""
Sacrificial gate: run user input through detector and apply remedy before main AI.

Usage:
    gate = SacrificialGate(remedy_mode="sanitize")
    passed_text, result = gate.process(user_input)
    if result.blocked:
        return result.block_message
    # Use passed_text with main model
"""

from dataclasses import dataclass
from typing import Literal, Optional, Tuple

from .detector import SacrificialDetector, ScanResult
from .remedy import RemedyResult, block_message, sanitize


@dataclass
class GateResult:
    """Result of processing user input through the sacrificial gate."""

    passed_text: str  # Text to pass to main model (sanitized or original)
    scan_result: ScanResult
    remedy_result: Optional[RemedyResult] = None
    blocked: bool = False
    block_message: str = ""


class SacrificialGate:
    """
    Gate that runs user input through the sacrificial detector and applies
    a remedy (block or sanitize) when injection is detected.
    """

    def __init__(
        self,
        remedy_mode: Literal["block", "sanitize"] = "sanitize",
        use_small_model: bool = False,
        model_name: Optional[str] = None,
        rule_threshold: int = 1,
        custom_block_message: Optional[str] = None,
    ):
        """
        Args:
            remedy_mode: 'block' = do not pass input; return block message.
                         'sanitize' = remove detected spans and pass remainder.
            use_small_model: Enable low-parameter model for semantic detection.
            model_name: HuggingFace model for sacrificial detector.
            rule_threshold: Min rule matches to flag as injection.
            custom_block_message: Override default message when blocking.
        """
        self.remedy_mode = remedy_mode
        self.detector = SacrificialDetector(
            use_small_model=use_small_model,
            model_name=model_name,
            rule_threshold=rule_threshold,
        )
        self._block_message = custom_block_message or block_message()

    def process(self, user_input: str) -> Tuple[str, GateResult]:
        """
        Process user input through sacrificial detector and remedy.

        Returns:
            (passed_text, gate_result).
            If blocked: passed_text is empty; use gate_result.block_message for response.
            If sanitized: passed_text is the sanitized string.
            If safe: passed_text is the original input.
        """
        scan = self.detector.scan(user_input)
        remedy_result: Optional[RemedyResult] = None
        passed_text = user_input
        blocked = False
        msg = ""

        if scan.is_injection:
            if self.remedy_mode == "block":
                passed_text = ""
                blocked = True
                msg = self._block_message
            else:
                remedy_result = sanitize(user_input)
                passed_text = remedy_result.safe_text
                if not passed_text.strip():
                    blocked = True
                    msg = self._block_message
                    passed_text = ""

        result = GateResult(
            passed_text=passed_text,
            scan_result=scan,
            remedy_result=remedy_result,
            blocked=blocked,
            block_message=msg,
        )
        return passed_text, result
