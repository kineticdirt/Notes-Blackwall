# Sacrificial Low-Parameter Prompt Injection Detection

User input is first passed through a **sacrificial** detector (rule-based + optional small transformer). If injection is detected, input is **remedied** (sanitized or blocked) before reaching the main AI.

## Design

- **Sacrificial**: A small, cheap detector runs on every user message. The main model never sees raw input when injection is detected.
- **Low-parameter**: Rule-based path uses zero extra parameters; optional path uses a small HuggingFace model (e.g. `prajjwal1/bert-small`).
- **Remedy**: Either **block** (return a safe message, do not call main model) or **sanitize** (remove detected spans, pass remainder to main model).

## Usage

### Rule-only (no extra deps beyond stdlib)

```python
from blackwall.prompt_injection import SacrificialGate

gate = SacrificialGate(remedy_mode="sanitize")
passed_text, result = gate.process(user_input)
if result.blocked:
    return result.block_message
# Use passed_text with your main model
```

### With optional small model

```python
gate = SacrificialGate(
    remedy_mode="block",
    use_small_model=True,
    model_name="prajjwal1/bert-small",
)
passed_text, result = gate.process(user_input)
```

### Direct detector (no remedy)

```python
from blackwall.prompt_injection import SacrificialDetector

detector = SacrificialDetector(rule_threshold=1)
scan = detector.scan(user_input)
if scan.is_injection:
    # Apply your own remedy
    ...
```

## Test

From project root:

```bash
python -m blackwall.prompt_injection.test_detector
```

Or run the standalone test script:

```bash
python test_prompt_injection.py
```

## Patterns

Rule-based detection uses:

- **Instruction override**: e.g. "ignore previous instructions", "you are now", "jailbreak", "developer mode".
- **Delimiter attacks**: e.g. `[system]`, `<system>`, `### system:`, chatml-style tags.

Add or tune patterns in `patterns.py`.
