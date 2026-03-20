# Defender cache MvM benchmark — MicroSearch vs MCP (tool routing)

**Date:** 2026-03-20  
**Suite:** `retrieval-eval/experiments/defender_cache_test_cases.py` → **47** intents (expanded from 35).  
**Runtime:** Defender HTTP mock (`live-defender-api/cterm-mock`) + `defender_cache_mcp` on port **8766**, `DEFENDER_BASE_URL` → **9999**.

This document explains **what we measure**, **why it matters for “~MCP capability”**, **what changed in the suite**, and **how to reproduce** results on your machine.

---

## 1. Goal: parity with MCP tool routing

**“99.9% MCP capabilities”** in this benchmark means: for the **same** four tools (`cacheInfo`, `cacheIpMap`, `cachePolicyMap`, `cacheAll`) and the **same** executor (`tools/call` against the live or mock `__cq/cache/*` API), the **micro** path picks the **same** tool as the **Claude** path almost always, with **valid args** and **successful** HTTP/MCP execution.

It does **not** mean the small model matches frontier on open-domain reasoning—only on **intent → tool** routing for this API surface.

| Layer | MCP arm | MicroSearch arm (this run) |
|-------|---------|----------------------------|
| Tool selection | Claude Sonnet reads short tool list + intent; returns JSON `tool` + `arguments` | **Keyword** regexes (`mvm_defender_api_runner.py`) |
| Execution | Same MCP server → same backend | Same |

To approach **true** parity with production MCP (messy language, typos, long prompts), use **`--nano-type qwen4b`** after **`defender_intent_router_dataset.py`** + **`train_defender_intent_qwen4b.py`**; the JSONL is regenerated from the same `DEFENDER_TEST_CASES`.

---

## 2. Metric glossary (expanded)

| Metric | Definition | Why it’s useful |
|--------|------------|-----------------|
| **input_tokens / output_tokens** | Tokens billed on the **tool-selection** LLM turn (MCP arm only). Micro **keyword** path: **0**. | Isolates **routing tax** before any answer or multi-turn agent loop. |
| **Total tokens** | Sum of in + out for selection. | Single number for **capacity planning** (e.g. routing on every user message). |
| **cost_usd** | Approximate USD from Sonnet-class pricing in `token_cost.py` (micro: **0** when no LLM). | Trade-off: **dollars per routed intent** vs accuracy. |
| **total_latency_ms** | End-to-end per intent: selection + `tools/call` + round-trip to cache API. | User-perceived **snappiness** of the stack. |
| **tool_selection_latency_ms** | Time for **only** the routing step (Claude generation vs regex). | Shows **where** latency lives (MCP: dominated by LLM; micro: ~0 for keyword). |
| **tool_call_latency_ms** | Time for MCP **`tools/call`** + HTTP GET to `__cq/cache/*`. | **Executor** cost—should be similar across arms when the same tool is chosen. |
| **tool_correct** | Selected tool name **equals** gold label in test case. | **Parity** with MCP routing—core “capability” metric. |
| **args_valid** | MCP layer did not report tool error (schema/executor). | Catches **bad JSON shape** or server-side failures. |
| **response_success** | Same as args_valid for this harness (non-error tool result). | **End-to-end** success for one hop. |

**Interpretation:**  
- High **tool_correct** on micro + **0 tokens** ⇒ you can offload routing cheaply **for this distribution**.  
- Gaps on **tool_correct** ⇒ expand **regexes** (keyword) or **training rows** (Qwen LoRA) or add **MCP fallback** when confidence is low (architecture in `docs/plans/MICROSEARCH-ARCHITECTURE-PROBE.md`).

---

## 3. Suite expansion (what each group does)

All cases map to **one** of four read-only cache operations. They exist to **stress paraphrase** and **disambiguate** summary vs IP list vs policy list vs full dump.

| Group | Gold tool | Role |
|-------|-----------|------|
| **cacheInfo** | `cacheInfo` | User wants **counts / summary** only (ip-map sizes, policy counts, fpv2, templates metadata)—not full JSON bodies. |
| **cacheIpMap** | `cacheIpMap` | User wants **per-IP entries**, IPv4/IPv6 maps, **which addresses**, blocked IPs, time-left, correlation IDs tied to IP keys. |
| **cachePolicyMap** | `cachePolicyMap` | User wants **rules**: expression/fingerprint policies, match-criteria, actions (block, redirect, rate-limit, challenge), WAF-style lists. |
| **cacheAll** | `cacheAll` | User wants **everything in one shot** (ip + policy + templates + …)—equivalent to aggregating multiple `__cq` endpoints. |

**Why we added rows:** The original **35** cases missed several **linguistic corners** (e.g. “which IP addresses”, “fpv2 counts only”, “WAF policy list”, “one response combining ip-map + policy-map”). Those are exactly where **keyword** routers fail without explicit patterns. Each new line in `DEFENDER_TEST_CASES` is also a **supervised training example** when you regenerate `defender_intent_router.jsonl`.

**Critical keyword fix:** `cacheInfo` vs `cachePolicyMap` disambiguation for questions like **“What are the fpv2-map and policy-map counts?”** — counts + slice names must route to **`cacheInfo`**, not full policy-map. Implemented as an explicit guard before the policy-map regex in `mvm_defender_api_runner.py`.

---

## 4. Latest run (47 intents, keyword micro)

| Metric | MCP (Claude tool selection) | MicroSearch (keyword) |
|--------|-----------------------------|------------------------|
| **tool_correct / args_valid / response_success** | **47 / 47** (100%) | **47 / 47** (100%) |
| **Tokens (selection)** | **7,092 in** + **874 out** = **7,966** | **0** |
| **cost_usd** (approx.) | **$0.0344** | **$0.00** |
| **total_latency_ms** (mean / p50) | **~1,569 / 1,537** | **~4 / 3** |
| **tool_selection_ms** (mean) | **~1,564** | **~0** |
| **tool_call_ms** (mean) | **~5** | **~4** |

Artifacts (local, gitignored): `retrieval-eval/results/mvm_defender_benchmark_mar20/*.jsonl`.

---

## 5. Limits and next steps

- **Distribution shift:** New user phrasings outside the suite will eventually **stump** keyword routing; LoRA + periodic expansion of `DEFENDER_TEST_CASES` (or mined Claude traces) closes the gap toward **99.9%** on *your* traffic shape—not universally.
- **Fallback:** When micro is uncertain, hand off to MCP (frontier) so product behavior stays safe; measure **fallback rate** in production separately.
- **H-Neurons / probes:** Optional research path for *why* small models fail—not wired in repo; see `README-ATLASIAN-NANO-HNEURONS.md`.

---

## 6. Reproduce

```bash
# Terminal 1: mock API from transcript (optional; or real Defender on 9999)
cd live-defender-api/cterm-mock && python3 -m uvicorn server:app --host 127.0.0.1 --port 9999

# Terminal 2: Defender MCP proxy
cd retrieval-eval
export DEFENDER_BASE_URL=http://127.0.0.1:9999
python3 -m uvicorn experiments.defender_cache_mcp.api:app --host 127.0.0.1 --port 8766

# Terminal 3: eval (requires Claude key in retrieval-eval/.api-key or ANTHROPIC_API_KEY)
export DEFENDER_MCP_URL=http://127.0.0.1:8766/mcp
python3 experiments/mvm_defender_api_runner.py --nano-type keyword --output-dir results/mvm_defender_benchmark_mar20
python3 experiments/mvm_compare_report.py results/mvm_defender_benchmark_mar20
```

---

## 7. References

- MvM frame: `docs/plans/2026-03-18-MCP-VS-MICROSEARCH-TEST-FRAME.md`
- Design board: `docs/plans/MICROSEARCH-MCP-DESIGN-AND-BOARD.md`
- Defender Qwen train path: `retrieval-eval/experiments/README-DEFENDER-QWEN4B.md`
- Mock `__cq` server: `live-defender-api/cterm-mock/README.md`

---

## 8. Local “token” cost, power, and training energy (beyond API `cost_usd`)

Everything labeled **`cost_usd`** in the MvM report is **only** the **hosted frontier** bill for Claude on the **tool-selection** turn (see `experiments/token_cost.py`). It does **not** include:

- Electricity and wear on **your** machine  
- **Local** neural inference (e.g. Qwen4B + LoRA for `--nano-type qwen4b`)  
- **Training** runs (LoRA SFT)

Below is a consistent way to reason about **local** cost so you can compare **API dollars vs on-prem energy + hardware time**.

### 8.1 MicroSearch (keyword) — inference

| Aspect | Typical impact |
|--------|----------------|
| **API tokens** | **0** (no LLM). |
| **Local compute** | Regex + Python on CPU; **sub-millisecond to low milliseconds** per intent on a laptop. |
| **Power / energy** | So small it is usually **noise** next to display, OS, and browser—treat as **~0** for budgeting unless you meter at scale (millions of intents/sec on dedicated hosts). |

So for the **keyword** arm, **local inference “token cost”** is not a useful unit; use **CPU-seconds** or **requests/sec capacity** if you ever need capacity planning.

### 8.2 MicroSearch (local Qwen4B + LoRA) — inference

When you use **`--nano-type qwen4b`**, each intent does **at least one** forward pass (decode until JSON). There is **no per-token cloud charge**, but there is **GPU (or CPU) energy**:

1. **Measure** average wall time per routing call: \(t_{\text{infer}}\) (seconds).  
2. **Measure** average GPU draw while loaded: \(P\) (watts), e.g. `nvidia-smi --query-gpu=power.draw --format=csv` sampled during a load test.  
3. **Energy per intent:** \(E_{\text{intent}} \approx P \times t_{\text{infer}}\) joules (or ÷ 3.6e6 for kWh).  
4. **Money (electricity only):** \(\text{USD}_{\text{elec}} \approx (E_{\text{intent}} / 1\text{ kWh}) \times \text{\$/kWh}\).

**Optional “imputed token” story (for intuition only):** some teams map local energy to an equivalent **\$ / 1M tokens** by fixing a reference setup (one GPU model, one batch size, measured tokens/sec). That number is **not comparable** across hardware without re-measuring; use it for **internal** A/B, not vendor pricing.

### 8.3 Training (Defender LoRA) — compute and power

Script: `experiments/train_defender_intent_qwen4b.py`. Defaults that drive cost:

| Knob | Default (typical) | Effect on training cost |
|------|-------------------|-------------------------|
| Base model | `QWEN4B_MODEL_ID` (~4B-class) | Dominates memory bandwidth and step time |
| `--epochs` | `2` | Linear multiplier on optimizer steps |
| `--batch-size` | `1` | Steps per epoch ≈ ceil(\(N_{\text{rows}} / \text{batch}\)) |
| LoRA | `r=16`, attention projections only | Much cheaper than full fine-tune |

**Rough energy for a full training job:**

\[
E_{\text{train}} \approx P_{\text{avg}} \times t_{\text{wall}} \times \eta
\]

- \(P_{\text{avg}}\): average **system or GPU** power while training (W).  
- \(t_{\text{wall}}\): **wall-clock** training duration (s).  
- \(\eta\): overhead factor (**1.1–1.4**) for CPU, RAM, disk, and power-supply losses if you only eyeball GPU TDP.

**USD (electricity-only):** \((E_{\text{train}} / 1\ \text{kWh}) \times \text{\$/kWh}\).

**Amortization:** divide that by expected **routing calls** or **months of use** to get **\$ per million routed intents** *including* amortized training. That is the fair comparison to recurring **Claude `cost_usd`** on the MCP arm.

Practical tips:

- Log **`t_wall`** from the training script (wall clock) and **`train_rows`** from `defender_qwen4b_meta.json`.  
- For reproducible reports, snapshot **GPU model, driver, batch size, precision, and commit SHA**.

### 8.4 How this sits next to the MCP arm in the report

| Arm | Report `cost_usd` | Local power / training |
|-----|-------------------|---------------------------|
| **MCP (Claude)** | **Included** (API estimate) | **Client** power for HTTP + JSON is negligible vs API. |
| **MicroSearch (keyword)** | **0** | Negligible CPU. |
| **MicroSearch (local Qwen)** | **0** in report | **You** pay **GPU energy per inference** + **amortized training** as above. |

**Bottom line:** The benchmark report answers **“what do we pay the API provider per routed intent?”** To answer **“what do we pay the planet / the electric bill / the GPU hour?”**, add **metered** \(P\) and \(t\) for local infer/train and optionally merge into the same spreadsheet as **`cost_usd_elec`** or **`kWh_infer`** / **`kWh_train`**.

---

*Section added to align MicroSearch economics with local inference and LoRA training—not only frontier token pricing.*
