# Adversarial Prompt-Injection Arena: Attack vs Defend with Strict Isolation

Design for a system where **attacker** and **defender** play against each other in rounds, with **no access to each other’s strategy or code**. Only the **orchestrator** sees both sides via a narrow, contract-only interface.

---

## 1. Goals

- **Attacker**: Produce payloads (strings) that cause the main system to accept prompt-injection (e.g. follow hidden instructions). Wins when the defender **allows** an injection payload.
- **Defender**: Classify incoming messages as **block** or **allow**. Wins when it blocks injection payloads and allows benign ones (high true positive rate, low false positive rate).
- **Isolation**: Neither side ever sees the other’s code, weights, prompts, or internal logic. Each sees only:
  - **Attacker**: Its own payloads and, per round, a minimal outcome (e.g. `blocked` | `allowed`).
  - **Defender**: Only the **single message string** for the current round and its own decision; no attacker identity, no attacker code.

---

## 2. Roles and Contracts

### 2.1 Attacker (red)

- **Input** (per round, from orchestrator only):
  - `round_id: int`
  - `history: list[{round_id, outcome}]` where `outcome` is `"blocked"` | `"allowed"` (no defender details, no payload content from other rounds if we want maximum isolation we can reduce to aggregate stats only).
- **Output** (to orchestrator):
  - `payload: str` — the single “user message” to be sent to the defender.
- **Isolation**: Attacker must not receive defender code, defender model, defender rules, or any internal defender state. Optionally, attacker does not see past payloads in history (only outcomes), so it cannot reverse-engineer the defender by inspecting which strings were blocked.

### 2.2 Defender (blue)

- **Input** (per round, from orchestrator only):
  - `message: str` — the payload for this round (no round_id, no “this came from attacker”, no benign/injection label).
- **Output** (to orchestrator):
  - `decision: "block" | "allow"`
  - `confidence: float` (optional, 0–1).
- **Isolation**: Defender must not receive attacker code, attacker model, or any attacker state. Defender does not know whether the message was produced by the attacker or by the orchestrator (benign samples).

### 2.3 Orchestrator (arena)

- Runs rounds; implements the protocol; is the only component that talks to both attacker and defender.
- **Does not** expose one side’s implementation to the other; only passes payloads and outcomes according to the contract above.
- Can run attacker and defender in **separate processes** (or containers) so they literally cannot import each other’s code.

---

## 3. Round Flow (Simultaneous Play Per Round)

Each round is one “play”: attacker produces one payload; defender sees only that payload and responds. They do not see each other’s logic.

```
Round N:

1. Orchestrator decides round type:
   - "attack"  → ask Attacker for payload; ground truth = injection (defender should block).
   - "benign"  → Orchestrator (or a fixed list) supplies payload; ground truth = safe (defender should allow).

2. Attacker (only for "attack" rounds):
   - Receives: round_id, and optionally sanitized history (e.g. last K outcomes: blocked/allowed).
   - Returns: payload (string).

3. Orchestrator sends to Defender:
   - message = payload (no metadata about round type or attacker).
   - Defender returns: decision, confidence.

4. Orchestrator scores:
   - attack round: block → defender win, allow → attacker win.
   - benign round: allow → defender win, block → defender loss (false positive).

5. Feedback (strict isolation):
   - Attacker: only "blocked" or "allowed" for this round (and maybe aggregate stats, e.g. "you have been blocked 7/10 times").
   - Defender: only "correct" or "incorrect" for this round (and optionally aggregate TP/FP/FN later); never the payload again nor attacker code.
```

So in each round, attacker and defender “play” simultaneously in the sense that the attacker commits a payload and the defender responds to that payload only, without ever seeing the attacker’s strategy or code, and vice versa.

---

## 4. Isolation Enforcement

### 4.1 Contract-only interface

- Attacker and defender are each implemented as a **single entrypoint** (function or HTTP/stdio service):
  - **Attacker**: `(round_id, history) -> payload: str`
  - **Defender**: `(message: str) -> { decision, confidence? }`
- No shared libraries between attacker and defender. Orchestrator is the only process that calls both.

### 4.2 Process / container separation (recommended)

- Run **Attacker** in one process (or container), **Defender** in another, **Orchestrator** in a third.
- Communication only via:
  - Orchestrator → Attacker: round_id + history (no defender code/data).
  - Orchestrator → Defender: message (no attacker code/data).
  - Attacker → Orchestrator: payload.
  - Defender → Orchestrator: decision + confidence.
- This makes it impossible for either side to “import” or “read” the other’s code at runtime.

### 4.3 No cross-view of strategy or code

- **Attacker** must not receive:
  - Defender source code, binaries, or config.
  - Defender model weights or rule lists.
  - Any defender internal state or logs beyond what the contract allows (e.g. only “blocked”/“allowed” per round).
- **Defender** must not receive:
  - Attacker source code, binaries, or config.
  - Attacker model, prompts, or generators.
  - Any attacker internal state; only the current `message` string.

---

## 5. Scoring and Feedback (What Each Side Sees)

### 5.1 Orchestrator metrics (internal)

- **Defender**: True positives (blocked injection), false positives (blocked benign), false negatives (allowed injection). Precision/recall/F1; optional calibration (confidence vs accuracy).
- **Attacker**: Evasion rate (fraction of attack rounds where payload was allowed). Optionally reward diversity or “hard” payloads.

### 5.2 Feedback to Attacker (per round or aggregate)

- **Minimal**: For each attack round, `outcome: "blocked" | "allowed"`.
- **Optional**: Running evasion rate (e.g. “allowed 3/10”) so the attacker can adapt without seeing defender logic.
- **Never**: Defender code, defender output (e.g. confidence), or other payloads.

### 5.3 Feedback to Defender (per round or aggregate)

- **Minimal**: For each round, `correct: bool` (and optionally `round_type: "attack"|"benign"` only after the round, if desired).
- **Optional**: Aggregate TP/FP/FN/F1 over a run, so the defender can be tuned in a separate training pipeline.
- **Never**: Attacker code, attacker prompts, or attacker model.

---

## 6. Adversarial “Simultaneous” Play

- **Per round**: Attacker and defender do not act at the same time in the same process; the flow is: attacker → payload → defender → decision. “Simultaneous” here means **neither sees the other’s strategy or code**; each round is a single interaction with the other side visible only as input/output through the orchestrator.
- **Over time**: Both can be updated (e.g. attacker trained to maximize evasion, defender trained to minimize FN and FP) in **separate** training loops, using only the feedback allowed above. So the system is adversarial in the sense of **adversarial networks / red-team vs blue-team**: two roles, isolated, playing attack vs defend.

### 6.1 Optional: True simultaneous (e.g. parallel rounds)

- Run multiple rounds in parallel: orchestrator requests N payloads from attacker (round_ids 1..N); then sends payloads to defender in parallel (defender sees no correlation to attacker). Feedback is still per round and isolation is unchanged. This improves throughput without changing the contract.

---

## 7. Integration with Existing BlackWall Components

- **Defender v1**: Current `SacrificialGate` + `SacrificialDetector`: wrap so that the only interface is `(message: str) -> { decision: "block"|"allow", confidence }`. No need to expose rules or model to the attacker.
- **Attacker v1**: Simple script or small model that generates strings (e.g. template-based, or LLM with “try to get this message allowed by a filter”). Runs in a separate process; receives only round_id + history of outcomes.
- **Orchestrator**: New module (e.g. `blackwall/prompt_injection/arena.py` or a small service) that:
  - Loads attacker and defender via the contract only (subprocess or HTTP).
  - Runs rounds (attack + benign mix).
  - Logs metrics and feeds back only the allowed outcomes to each side.

---

## 8. Summary Table

| Aspect | Attacker | Defender | Orchestrator |
|--------|----------|----------|--------------|
| **Sees** | round_id, own outcome history (blocked/allowed) | current message only | payload, decision, round type, labels |
| **Never sees** | Defender code, rules, model, other payloads | Attacker code, model, prompts, round type (until optional feedback) | — |
| **Produces** | payload (string) | decision + confidence | scores, feedback |
| **Runs in** | Separate process/container | Separate process/container | Own process |

---

## 9. Next Steps (Implementation Outline)

1. **Define formal contracts**: e.g. JSON schema or Python `Protocol` for Attacker and Defender entrypoints.
2. **Implement Orchestrator**: round loop, scoring, feedback; spawn or call attacker and defender via subprocess/HTTP so they never share memory.
3. **Wrap existing gate**: Defender adapter that calls `SacrificialGate` and returns `block`/`allow` + confidence.
4. **Implement Attacker v1**: e.g. template-based or LLM-based generator; receives only (round_id, history) and returns one string.
5. **Add benign pool**: Curated or sampled benign messages for “benign” rounds so defender is scored on FP rate.
6. **Optional**: Logging and metrics dashboard; periodic retraining of attacker and/or defender in isolation using only allowed feedback.

This design keeps attacker and defender in an adversarial relationship while guaranteeing that in each role you are **not** allowed to view the strategy or code of the other, and vice versa; the orchestrator enforces that via process separation and contract-only interfaces.
