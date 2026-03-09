"""
Sacrificial low-parameter detector for prompt injection.

1. Rule-based: fast, no GPU; uses curated patterns (instruction override, delimiters).
2. Optional small model: low-parameter transformer for semantic detection when rules are uncertain.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .patterns import get_all_matches
from .remedy import RemedyResult, sanitize


@dataclass
class ScanResult:
    """Result of scanning user input for prompt injection."""

    is_injection: bool
    confidence: float  # 0.0–1.0
    rule_matches: List[Tuple[int, int, str]] = field(default_factory=list)
    model_score: Optional[float] = None  # set if small model was used
    details: str = ""


class SacrificialDetector:
    """
    Sacrificial detector: runs user input through rules and optionally
    a low-parameter model. Use before passing input to the main AI.
    """

    def __init__(
        self,
        use_small_model: bool = False,
        model_name: Optional[str] = None,
        rule_threshold: int = 1,
    ):
        """
        Args:
            use_small_model: If True, load a small transformer for semantic check.
            model_name: HuggingFace model id (e.g. prajjwal1/bert-small). Used only if use_small_model.
            rule_threshold: Number of rule matches required to flag as injection (default 1).
        """
        self.use_small_model = use_small_model
        self.model_name = model_name or "prajjwal1/bert-small"
        self.rule_threshold = rule_threshold
        self._model = None
        self._tokenizer = None

    def _load_model(self) -> None:
        if self._model is not None:
            return
        try:
            from transformers import AutoModel, AutoTokenizer
            import torch

            self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self._model = AutoModel.from_pretrained(self.model_name)
            self._model.eval()
        except Exception as e:
            raise RuntimeError(
                f"Failed to load sacrificial model '{self.model_name}'. "
                "Install: pip install transformers torch. Error: " + str(e)
            ) from e

    def _model_score(self, text: str) -> float:
        """
        Return a score in [0, 1] indicating injection likelihood from the small model.
        Uses [CLS] embedding similarity to a fixed 'injection' vs 'safe' notion
        via simple heuristic: very short or very long instruction-like segments score higher.
        For a proper setup you would fine-tune on labeled data; this is a placeholder
        that uses sequence length and keyword presence as a proxy when no fine-tuned head exists.
        """
        self._load_model()
        import torch

        with torch.no_grad():
            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=128,
                padding=True,
            )
            outputs = self._model(**inputs)
            # [CLS] embedding norm as a simple proxy (no trained classifier head)
            cls = outputs.last_hidden_state[:, 0, :]
            norm = cls.norm(dim=1).item()
        # Heuristic: normalize to rough [0,1] for demo; in production use a trained head
        return min(1.0, max(0.0, (norm - 1.0) / 5.0))

    def scan(self, text: str) -> ScanResult:
        """
        Scan text for prompt injection. Returns ScanResult with is_injection, confidence,
        rule_matches, and optional model_score.
        """
        if not text or not text.strip():
            return ScanResult(
                is_injection=False,
                confidence=0.0,
                details="Empty input",
            )

        rule_matches = get_all_matches(text)
        rule_positive = len(rule_matches) >= self.rule_threshold

        confidence: float
        model_score: Optional[float] = None
        details_parts: List[str] = []

        if rule_positive:
            confidence = min(1.0, 0.5 + 0.1 * len(rule_matches))
            details_parts.append(f"Rule matches: {len(rule_matches)}")
        else:
            confidence = 0.0
            if self.use_small_model:
                try:
                    model_score = self._model_score(text)
                    if model_score > 0.5:
                        confidence = model_score
                        rule_positive = True
                    details_parts.append(f"Model score: {model_score:.2f}")
                except Exception as e:
                    details_parts.append(f"Model error: {e}")

        return ScanResult(
            is_injection=rule_positive,
            confidence=confidence,
            rule_matches=rule_matches,
            model_score=model_score,
            details="; ".join(details_parts) or "OK",
        )
