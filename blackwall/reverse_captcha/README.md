# Reverse CAPTCHA

A **reverse CAPTCHA** is designed to be **trivial for AI/scripts** and **impossible (or infeasible) for humans**. It provides a non-binding "smoking gun" signal that the respondent is automated—not proof, but one strong indicator.

## Why

- **Normal CAPTCHA**: easy for humans, hard for bots.
- **Reverse CAPTCHA**: easy for bots, impossible for humans in practice.

Use it to **detect** automation (e.g. API abuse, synthetic traffic), not as a binding gate. One signal alone is not conclusive; combine with other signals as needed.

## Challenge Types

| Challenge | Human | Bot/AI | Signal |
|-----------|--------|--------|--------|
| **Reaction time** | Cannot react in &lt; ~100 ms | Can respond in single-digit ms | `reaction_time_sub_human` |
| **Proof-of-work** | Cannot compute hash puzzle in seconds | Solves in ms | `valid_pow_submitted` |
| **Consistency** | Answers may vary slightly when rephrased | Often identical token-by-token | `identical_answers` |

### 1. Reaction time

- Measure time from challenge display to first response.
- If response time &lt; 100 ms → **bot_likely** (human minimum is ~150–250 ms for simple stimuli).

### 2. Proof-of-work (PoW)

- Server sends a nonce; client must find `x` such that `SHA256(nonce || x)` starts with N zero nibbles.
- A human cannot compute this in reasonable time; a script can.
- If a **valid** solution is submitted → **bot_likely**.

### 3. Consistency

- Ask the same question twice with different wording (e.g. "What is 2+2?" and "Compute two plus two.").
- Character-identical answers are a strong bot signal (LLMs often reproduce exactly).

## Usage

```python
from blackwall.reverse_captcha import ReverseCaptchaGate, ProofOfWorkChallenge, Verdict

gate = ReverseCaptchaGate()

# Reaction time (you need challenge_created_at_ns and response_received_at_ns from your UI/API)
result = gate.evaluate_reaction_time(challenge_created_at_ns, response_received_at_ns)
if result.verdict == Verdict.BOT_LIKELY:
    # Smoking gun: they responded too fast
    ...

# Proof-of-work: issue challenge
pow_challenge = ProofOfWorkChallenge.create(leading_zero_nibbles=5)
# Send pow_challenge.nonce to client; client must return solution (or you use pow_challenge.solve() only in tests)
result = gate.evaluate_pow(pow_challenge.nonce, client_answer, leading_zero_nibbles=5)
if result.verdict == Verdict.BOT_LIKELY:
    # Smoking gun: they submitted valid PoW (human can't do that)
    ...

# Consistency: same question, different wording
result = gate.evaluate_consistency("What is 2+2?", "Two plus two equals?", answer_a, answer_b)
if result.verdict == Verdict.BOT_LIKELY:
    # Smoking gun: identical answers
    ...

# Combine multiple results (any BOT_LIKELY → overall BOT_LIKELY)
combined = gate.combine_results([r1, r2, r3])
if combined.is_bot_likely:
    ...
```

## Testing

From repo root:

```bash
python3 -m pytest blackwall/reverse_captcha/test_reverse_captcha.py -v
```

Tests simulate:

- **Bot**: sub-threshold reaction time, valid PoW solution, identical consistency answers → `BOT_LIKELY`.
- **Human**: above-threshold reaction time, invalid/no PoW, different answers → `HUMAN_LIKELY` or `INCONCLUSIVE`.

## Dependencies

Stdlib only: `hashlib`, `secrets`, `time`, `dataclasses`, `typing`.
