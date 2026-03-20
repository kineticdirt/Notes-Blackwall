"""
Token cost for MvM comparison. Approximate USD from input/output token counts.
No secrets; pricing from public Anthropic API docs (e.g. Claude Sonnet ~$3/1M in, $15/1M out).
"""
from __future__ import annotations

# Per-million-token USD (approximate; update when model or pricing changes)
CLAUDE_SONNET_INPUT_PER_1M = 3.0
CLAUDE_SONNET_OUTPUT_PER_1M = 15.0


def token_cost_usd(
    input_tokens: int,
    output_tokens: int,
    model: str = "claude-sonnet-4-20250514",
) -> float:
    """Return approximate cost in USD for the given token counts."""
    if "sonnet" in model.lower():
        return (input_tokens / 1_000_000 * CLAUDE_SONNET_INPUT_PER_1M) + (
            output_tokens / 1_000_000 * CLAUDE_SONNET_OUTPUT_PER_1M
        )
    # Fallback: same as Sonnet
    return (input_tokens / 1_000_000 * CLAUDE_SONNET_INPUT_PER_1M) + (
        output_tokens / 1_000_000 * CLAUDE_SONNET_OUTPUT_PER_1M
    )
