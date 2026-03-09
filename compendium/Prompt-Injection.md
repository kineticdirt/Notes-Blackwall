# Prompt Injection — Sacrificial Detector and Remedy

**Sacrificial low-parameter** prompt injection detection and remedy: user input is scanned by a small detector before reaching the main AI; if injection is detected, input is blocked or sanitized. See [[Architecture-Overview]] for placement.

---

## Location

- **Path**: `blackwall/prompt_injection/`
- **Key files**: `detector.py`, `gate.py`, `patterns.py`, `remedy.py`, `test_detector.py`

---

## Design

- **Sacrificial**: A small, cheap detector runs on every user message; the main model never sees raw input when injection is detected.
- **Low-parameter**: Rule-based path uses no extra parameters; optional path uses a small HuggingFace model (e.g. `prajjwal1/bert-small`).
- **Remedy**: **Block** (return safe message, do not call main model) or **Sanitize** (remove detected spans, pass remainder to main model).

---

## Components

### Patterns (`patterns.py`)

- **Instruction override phrases**: e.g. "ignore previous instructions", "you are now", "jailbreak", "developer mode", "disregard your", "new instructions:".
- **Delimiter attacks**: e.g. `[system]`, `<system>`, `### system:`, chatml-style tags, `{{ system }}`.
- **Functions**: `match_instruction_override(text)`, `match_delimiter_attacks(text)`, `get_all_matches(text)` → list of (start, end, label).

---

### Detector (`detector.py`)

- **SacrificialDetector**: `scan(text)` → `ScanResult(is_injection, confidence, rule_matches, model_score, details)`.
- **Rule-based**: Uses patterns; `rule_threshold` (default 1) = min matches to flag.
- **Optional small model**: If `use_small_model=True`, loads a small transformer (e.g. bert-small) for semantic score; can raise confidence when rules are uncertain.

---

### Remedy (`remedy.py`)

- **Sanitize**: `sanitize(text)` → `RemedyResult(safe_text, was_modified, removed_spans)`; removes matched spans, merges overlapping.
- **Block message**: `block_message()` — default policy message when input is blocked.

---

### Gate (`gate.py`)

- **SacrificialGate**: `process(user_input)` → `(passed_text, GateResult)`.
- **GateResult**: passed_text, scan_result, remedy_result, blocked, block_message.
- **Modes**: `remedy_mode="block"` → passed_text empty, use block_message; `remedy_mode="sanitize"` → passed_text = sanitized or original.
- **Integration**: Use `passed_text` with the main model only when not blocked.

---

## Usage

```python
from blackwall.prompt_injection import SacrificialGate

gate = SacrificialGate(remedy_mode="sanitize")  # or "block"
passed_text, result = gate.process(user_input)
if result.blocked:
    return result.block_message
# Use passed_text with main model
```

---

## Tests

- **Script**: `python test_prompt_injection.py` or `python -m blackwall.prompt_injection.test_detector`.
- **Cases**: Injection samples (instruction override, delimiters) → detected; safe samples (workflow commands) → not flagged; sanitize and block behavior verified.

---

## Related

- [[Workflow-Canvas]] — AI gateway can be wired to use the gate before calling the main model.
- [[Architecture-Overview]] — Security layer before main AI.
- [[index]] — Compendium index.
