# Cursor Command: Rigorous Hypothesis Test

Use this when you want the agent to **tentatively test a hypothesis** in the most challenging and rigorous way: probe with real requests, generate a hypothetical solution, test it, and add intent-based test cases (not hardcoded). Report **in chat only**—no report markdown files.

---

## Inline command (copy into Cursor chat)

```
Rigorous hypothesis test. (1) Identify or infer the hypothesis we're testing (e.g. idempotency, auth, schema under load). (2) Probe with curl/real requests first—no mocks—and record status, headers, body, timing. (3) Propose a hypothetical solution and label it as such. (4) Re-probe under the hardest relevant conditions (concurrency, retries, bad input, etc.); goal is success in the most challenging setting, not just happy path. (5) Add intent-based test cases: assert user/system intent (e.g. "duplicate requests → at most one side effect", "401 when unauthenticated"), derive expectations from spec/contract where possible, avoid hardcoded strings and magic numbers; document which hypothesis and rigorous condition each test targets. (6) Report directly in the chat (do not create report markdowns or files): hypothesis, before/after probe results, whether it holds under rigor, and what's still missing if it doesn't. Do not claim success if it only passes the easy case.
```

---

## Full workflow (same content, expanded)

1. **Identify the hypothesis or problem**
   - State what we're trying to prove or disprove (e.g. "API X is idempotent under retries", "service Y tolerates network partition", "endpoint Z returns consistent schema under load").
   - If no hypothesis is given, infer it from the codebase or the system under test (e.g. from OpenAPI spec, README, or existing tests). Call out the inferred hypothesis clearly.

2. **Probe with real requests first**
   - Use `curl`, `httpie`, or equivalent to hit the real system (local or staging). No mocks for this step.
   - Exercise the behavior in question: success path, error path, boundary inputs, duplicate requests, malformed input, or whatever the hypothesis implies.
   - Capture and note: status codes, headers, body shape, timing, and any non-determinism. If the system isn't running, document how to start it and what URL/base path to use, then run the requests once the environment is available.

3. **Generate a hypothetical solution**
   - Propose a minimal change or design that would make the hypothesis hold (code, config, or contract). Label it explicitly as "hypothetical" and tie it to the probe results (e.g. "Given the 500 on duplicate POST, the hypothesis is that adding idempotency keys will fix it").

4. **Test the hypothesis rigorously**
   - Run the probe again after applying the hypothetical solution (or against a branch that has it). Compare before/after.
   - Prefer the most challenging conditions that match real use: concurrent requests, retries, large payloads, bad auth, missing headers, or rate limits—depending on what the hypothesis is about. The goal is to see it **succeed in the hardest relevant setting**, not just in the happy path.

5. **Write intent-based test cases (no hardcoding)**
   - Add or extend tests that encode **user/system intent**, not fixed strings or magic numbers. Examples of intent: "repeated identical requests produce at most one side effect", "unauthenticated requests are rejected with 401", "response schema matches the declared contract for all success responses".
   - Parameterize or derive assertions from spec/contract (e.g. OpenAPI, shared constants, or env) so the tests stay valid when URLs, status codes, or messages change as long as intent is preserved.
   - Prefer property-style or contract-style checks where possible (e.g. "every 2xx response has these required fields") rather than "response equals this exact JSON".
   - Document in the test file what hypothesis each test supports and what "rigorous" condition it represents (e.g. concurrency, retries, invalid input).

6. **Report (in chat only—no report markdown files)**
   - Give the report directly in the chat: hypothesis, probe results (before/after), whether the hypothesis holds under the rigorous conditions, and any new edge cases or failures found. If the system did not pass under the hard case, do not claim success; state what would be needed to get there. Do not create a separate report markdown or file; put all of this in the conversation.

---

## Usage

- **Quick:** Paste the inline command above into Cursor chat and append the hypothesis or system (e.g. "Apply to `/api/orders` and the hypothesis that duplicate POSTs are deduplicated by `Idempotency-Key`.").
- **As a rule:** Put the inline command or this file in `.cursor/rules` so the agent follows it when you say "rigorous hypothesis test" or "test hypothesis with curl and intent-based tests."

---

## Intent

The goal is **not** to see a single green test run; it is to see the system **succeed in the most challenging and rigorous settings** implied by the hypothesis. Tests should reflect **intent** (what the user or system is trying to guarantee), not brittle hardcoded values. **Reporting:** give the report in the chat only; do not create report markdown files or separate report artifacts.
