# Neural & Related Technologies — Tangential Reference

Technologies (frameworks, papers, systems) that are **tangentially related** to Notes - Blackwall: multi-agent coordination, prompt-injection defense, text/content protection, memory/context, belief-style state, and agent tooling. Not an endorsement; use for research and comparison.

**Recency:** This doc focuses on **2022–2025** (last 3 years). Older foundations (e.g. AlexNet-era, early BERT/GPT-2) are omitted; the goal is **cutting-edge** and larger recent changes in LLM/agent/security/memory.

---

## 1. Multi-agent / LLM coordination (2022+)

| Name | Year | What it is |
|------|------|------------|
| **TalkHier** (Talk Structurally, Act Hierarchically) | 2025 | Structured communication + hierarchical refinement for multi-agent LLMs; outperforms o1, AgentVerse, ReAct on QA and text gen. [arXiv 2502.11098] |
| **AgentNet** (NIPS 2025) | 2025 | Decentralized, privacy-preserving; dynamic DAG topologies, retrieval-augmented adaptive learning, agent specialization. [arXiv 2504.00587], [GitHub: zoe-yyx/AgentNet] |
| **Agentic Neural Networks (ANN)** | 2025 | Agents = nodes, layers = teams; "textual backpropagation" to refine roles/prompts/coordination. [arXiv 2506.09046] |
| **Graph-of-Agents (GoA)** | 2025 | Graph-based multi-agent; node sampling, directional message passing, response aggregation; 3 agents beat 6 on MMLU/GPQA/HumanEval. [OpenReview 34cANdsHKV] |
| **Optima** | 2024 | Generate-rank-select-train with RL; ~2.8x gains with &lt;10% token overhead on info-exchange (Llama 3 8B). [arXiv 2410.08115] |
| **ReDel** | 2024 | Toolkit for recursive multi-agent systems; delegation, custom tools, event logging, debugging. [arXiv 2408.02248] |
| **AgentsNet** | 2025 | Benchmark for multi-agent coordination; 100+ agents, graph topologies; frontier LLMs degrade at scale. [arXiv 2507.08616] |
| **LangGraph** | 2024+ | Workflow = directed graph; state, checkpointing, persistence; wraps CrewAI/AutoGen. [LangChain] |
| **CrewAI** | 2024+ | Role-based crews; short/long-term and entity memory; parallel/sequential flows. [CrewAI] |
| **AutoGen** (Microsoft) | 2023+ | Conversation-based; UserProxy/Assistant; multi-turn. [AutoGen] |

**Tangent to BlackWall:** Your coordinator + ledger + subagents (cleanup/test/doc) are file-based and rule-driven; these add neural/graph/benchmark perspectives and graph-based state for comparison.

---

## 2. Prompt-injection detection / defense (2022+)

| Name | Year | What it is |
|------|------|------------|
| **PromptShield** | 2025 | Deployable detector + benchmark; curated conversational/application-structured data; strong in low-FPR regimes. [arXiv 2501.15145] |
| **DataSentinel** | 2025 | Game-theoretic; minimax optimization to detect adaptive injected prompts; gradient-based. [arXiv 2504.11358] |
| **PromptSleuth** | 2025 | Semantic intent invariance; task-level reasoning; adversarial intent constant across surface forms. [arXiv 2508.20890] |
| **SecAlign** | 2024 | Training-time: preference optimization for secure vs insecure outputs; ~0% attack success, generalizes to unknown attacks. [arXiv 2410.05451] |
| **DefensiveTokens** | 2024 | Test-time: optimized token embeddings inserted before input; security toggle without changing model. [arXiv 2411.00459] |
| **PromptGuard** | 2025 | Multi-layer: gatekeeping, structured prompts, semantic validation, refinement; regex + MiniBERT; ~67% injection reduction. [Nature Sci. Reports] |
| **Attention-based** (Rennervate-style) | 2025 | Token-level detection/sanitization for **indirect** prompt injection; attention features; 2-step pooling. [arXiv 2512.08417] |

**Tangent to BlackWall:** Your prompt-injection gate is rule-based (patterns, optional small-model score). These are neural alternatives or complements for detection/defense.

---

## 3. Indirect & multimodal prompt injection (2023+)

| Name | Year | What it is |
|------|------|------------|
| **CrossInject** | 2025 | Cross-modal injection: adversarial perturbations in image + text to manipulate multimodal agents; ~30%+ higher success than prior. [arXiv 2504.14348] |
| **Spotlighting** | 2024 | Defense: input transformations to signal provenance; reduces indirect injection success from &gt;50% to &lt;2%. [arXiv 2403.14720] |
| **Multimodal PI survey** | 2025 | Risks and defenses for modern LLMs; all tested models vulnerable; Claude 3 relatively more robust. [arXiv 2509.05883] |
| **External content injection** | 2023 | Instructions in web/external content hijack outputs; LLMs don’t distinguish info vs instructions. [arXiv 2312.14197] |

**Tangent to BlackWall:** Your gate is text-only. These address image/document/context-based injection and provenance.

---

## 4. Text watermarking / content protection (2022+)

| Name | Year | What it is |
|------|------|------------|
| **Black-box watermark detection** | 2024/25 | Rigorous statistical tests detect presence/params of watermarks with limited API queries; schemes more detectable than thought. [arXiv 2405.20777] |
| **Water-Probe / Water-Bag** | 2024 (ICLR 2025) | Crafted prompts identify watermarked LMs (consistent bias per key); Water-Bag merges keys for better imperceptibility. [arXiv 2410.03168] |
| **PostMark** (EMNLP 2024) | 2024 | Post-hoc watermarking without logit access; third-party; more robust to paraphrasing across 8 baselines, 5 LMs. [arXiv 2406.14517] |
| **Publicly-detectable** | 2023 | Cryptographic signatures in output; rejection sampling + error correction; anyone can detect, no secret. [arXiv 2310.18491] |
| **Radioactivity (NeurIPS 2024)** | 2024 | Detect watermarks in fine-tuned models trained on watermarked data; high confidence with as little as 5% watermarked text. [arXiv 2402.14904] |

**Tangent to BlackWall:** Your stack does text watermarking/poisoning and detection (e.g. nightshade-tracker, UnifiedProcessor). These are academic/industrial parallels and possible refinements.

---

## 5. Memory / long-context (2022+)

| Name | Year | What it is |
|------|------|------------|
| **M+** (MemoryLLM extension) | 2025 | Long-term memory + co-trained retriever; extends effective retention from ~20k to 160k+ tokens. [arXiv 2502.00592] |
| **LWM** (Large World Model) | 2024 | Blockwise RingAttention; 7B model, text+video **1M+ tokens**; competitive retrieval vs GPT-4/Gemini. [NeurIPS 2024, arXiv 2402.08268] |
| **Samba** | 2024 | Mamba + Sliding Window Attention; unlimited-context; 1M zero-shot, 256K fine-tuned; 3.73x throughput vs Transformer at 128K. [arXiv 2406.07522] |
| **EpMAN** | 2025 | Episodic memory attention; reweight decoder to KV cache; 16k–256k. [arXiv 2502.14280] |
| **InfLLM** | 2024 | Training-free; memory units + lookup; **1,024K** tokens without fine-tuning. [arXiv 2407.12117] |
| **SELF-PARAM** | 2024 | Context in parameters (no extra params); KL minimization; fast update and retention. [arXiv 2410.00487] |
| **MEMO** (NeurIPS 2024) | 2024 | Activation offload to CPU per layer; token-wise recomputation; long-context training. |
| **DMC** (NeurIPS 2024) | 2024 | KV cache compression per head/layer; ~7x throughput, 4x compression. |

**Tangent to BlackWall:** Your notes/progress MCP and “save progress / read progress” are explicit external state. These are in-model or inference-level memory/context mechanisms for comparison.

---

## 6. Belief / uncertainty / calibration (2022+)

| Name | Year | What it is |
|------|------|------------|
| **Uncertainty survey (LLMs)** | 2025 | First systematic comparison of uncertainty measurement and calibration for LLMs; benchmarks, hallucination focus. [arXiv 2504.18346] |
| **UniCR** | 2025 | Unified calibration: sequence likelihood, self-consistency, retrieval, tool feedback → correctness probabilities; conformal risk control; API-only. [arXiv 2509.01455] |
| **Linguistic verbal uncertainty (LVU)** | 2025 | Across 80 models: LVU outperforms token-prob and numerical verbal uncertainty; better on reasoning than knowledge. [OpenReview] |
| **IB-EDL** | 2025 | Evidential deep learning + information bottleneck; reduces overconfidence in fine-tuned LLMs on small data. [arXiv 2502.06351] |
| **Hidden-layer uncertainty** | 2024 | Supervised uncertainty from activations; transfer across black-box to white-box. [arXiv 2404.15993] |

**Tangent to BlackWall:** Your BDH-style beliefs (likelihood_percent, evidence, logic) are explicit structured state. These are cutting-edge LLM calibration/uncertainty for comparison.

---

## 7. LLM reasoning & agentic systems (2024–2025)

| Name | Year | What it is |
|------|------|------------|
| **Frontiers in LLM reasoning survey** | 2025 | Inference scaling vs learning-to-reason; standalone vs agentic (tools); DeepSeek-R1, OpenAI Deep Research, Manus; GRPO/PPO, generator-evaluator, debate. [arXiv 2504.09037] |
| **ARTIST** (Microsoft) | 2025 | Agentic reasoning + RL for tool use; when/how/which tools; outcome-based RL, no step supervision; ~22% gain on math and function calling. [Microsoft Research] |
| **Learning-to-reason** | 2024+ | Shift from CoT to trained reasoners (e.g. DeepSeek-R1) and agentic workflows with tools. [Survey 2504.09037] |

**Tangent to BlackWall:** Your coordinator + MCP tools align with agentic tool use; these are the frontier formulations (RL, scaling, tool integration).

---

## 8. RAG (retrieval-augmented generation) (2024–2025)

| Name | Year | What it is |
|------|------|------------|
| **RAG survey (architectures & robustness)** | 2025 | Retriever- vs generator-centric, hybrid, robustness; retrieval optimization, context filtering, efficiency. [arXiv 2506.00054] |
| **ImpRAG** | 2025 | Implicit queries: retrieval + generation without explicit query string; 3.6–11.5% EM gain on unseen knowledge tasks. [arXiv 2506.02279] |
| **GraphRAG** | 2024+ | Graph-structured indexing/retrieval/generation; entity relations. [Survey 2501.00309, 2408.08921] |
| **RAG systematic review** | 2025 | 128 papers; evaluation, datasets, architectures; hallucination, robustness, efficiency. [arXiv 2508.06401] |

**Tangent to BlackWall:** Your workflow-canvas BDH and RAG nodes sit in this space; graph and implicit-query directions are relevant.

---

## 9. Model Context Protocol (MCP) & agent tooling

| Name | Year | What it is |
|------|------|------------|
| **Anthropic advanced tool use** | 2025 | Three beta features: **Tool Search Tool** (discover tools on-demand, ~85% token reduction vs loading all definitions); **Programmatic Tool Calling** (invoke tools from code execution to reduce context bloat); **Tool Use Examples** (teach usage patterns beyond JSON schema). [Anthropic engineering: advanced-tool-use] |
| **Model Context Protocol (MCP)** | 2024 | JSON-RPC; tools, prompts, resources; stdio/HTTP/SSE; sampling for agentic behavior. [modelcontextprotocol.io] |
| **Anthropic + MCP (code execution)** | 2024+ | Code execution via MCP; agents handle hundreds/thousands of tools with lower token use. [Anthropic: code-execution-with-mcp] |
| **OpenAI Agents + MCP** | 2024+ | MCP support in OpenAI agents Python stack. [openai.github.io/openai-agents-python] |

**Tangent to BlackWall:** You already use MCP (notes server, tools). Advanced tool use (search, programmatic calls, examples) is the cutting-edge layer for scaling tool libraries without blowing context. **Extended summary and application:** [docs/ANTHROPIC_ADVANCED_TOOL_USE.md](ANTHROPIC_ADVANCED_TOOL_USE.md).

---

## 10. Quick reference by BlackWall area

| Your area | Tangential neural / related tech (2022+) |
|-----------|------------------------------------------|
| **Coordinator, ledger, subagents** | TalkHier, AgentNet, ANN, Graph-of-Agents, Optima, ReDel, LangGraph, CrewAI, AutoGen |
| **Prompt-injection gate** | PromptShield, DataSentinel, PromptSleuth, SecAlign, DefensiveTokens, PromptGuard, attention-based (indirect) |
| **Indirect / multimodal injection** | CrossInject, Spotlighting, multimodal PI survey |
| **Text protection / watermarking** | Black-box detection, Water-Probe/Water-Bag, PostMark, publicly-detectable, Radioactivity |
| **Notes / progress / context** | M+, LWM, Samba, EpMAN, InfLLM, SELF-PARAM, MEMO, DMC |
| **Beliefs (likelihood, evidence)** | UniCR, uncertainty survey, LVU, IB-EDL |
| **Reasoning & tools** | LLM reasoning survey, ARTIST, learning-to-reason |
| **RAG / BDH** | RAG survey, ImpRAG, GraphRAG |
| **MCP tools & Cursor** | Anthropic advanced tool use (Tool Search, Programmatic Tool Calling, Tool Use Examples), MCP spec, Anthropic code execution with MCP, OpenAI agents + MCP |

---

## 11. Links (representative; 2022+)

**Multi-agent:** TalkHier 2502.11098, AgentNet 2504.00587, ANN 2506.09046, Graph-of-Agents OpenReview 34cANdsHKV, Optima 2410.08115, ReDel 2408.02248, AgentsNet 2507.08616. **Prompt injection:** PromptShield 2501.15145, DataSentinel 2504.11358, PromptSleuth 2508.20890, SecAlign 2410.05451, DefensiveTokens 2411.00459, attention-based 2512.08417. **Indirect/multimodal:** CrossInject 2504.14348, Spotlighting 2403.14720, multimodal survey 2509.05883. **Watermarking:** Black-box 2405.20777, Water-Probe 2410.03168, PostMark 2406.14517, publicly-detectable 2310.18491, Radioactivity 2402.14904. **Memory/long-context:** M+ 2502.00592, LWM 2402.08268, Samba 2406.07522, EpMAN 2502.14280, InfLLM 2407.12117, SELF-PARAM 2410.00487. **Uncertainty/calibration:** Survey 2504.18346, UniCR 2509.01455, IB-EDL 2502.06351, hidden-layer 2404.15993. **Reasoning/agentic:** Survey 2504.09037, ARTIST (Microsoft). **RAG:** Survey 2506.00054, ImpRAG 2506.02279, GraphRAG 2501.00309/2408.08921, review 2508.06401. **MCP:** Anthropic [advanced-tool-use](https://www.anthropic.com/engineering/advanced-tool-use) (Tool Search, Programmatic Tool Calling, Tool Use Examples), [code-execution-with-mcp](https://www.anthropic.com/engineering/code-execution-with-mcp), [modelcontextprotocol.io](https://modelcontextprotocol.io), OpenAI agents.

---

## 12. All entries (full list with links)

Every technology from §§1–9 in one list with direct links. arXiv IDs link to `https://arxiv.org/abs/XXXX.XXXXX`.

### Multi-agent / LLM coordination
| Name | Year | Link |
|------|------|------|
| TalkHier (Talk Structurally, Act Hierarchically) | 2025 | [arXiv 2502.11098](https://arxiv.org/abs/2502.11098) |
| AgentNet (NIPS 2025) | 2025 | [arXiv 2504.00587](https://arxiv.org/abs/2504.00587), [GitHub zoe-yyx/AgentNet](https://github.com/zoe-yyx/AgentNet) |
| Agentic Neural Networks (ANN) | 2025 | [arXiv 2506.09046](https://arxiv.org/abs/2506.09046) |
| Graph-of-Agents (GoA) | 2025 | [OpenReview 34cANdsHKV](https://openreview.net/forum?id=34cANdsHKV) |
| Optima | 2024 | [arXiv 2410.08115](https://arxiv.org/abs/2410.08115) |
| ReDel | 2024 | [arXiv 2408.02248](https://arxiv.org/abs/2408.02248) |
| AgentsNet | 2025 | [arXiv 2507.08616](https://arxiv.org/abs/2507.08616) |
| LangGraph | 2024+ | [LangChain LangGraph](https://langchain-ai.github.io/langgraph/) |
| CrewAI | 2024+ | [CrewAI](https://www.crewai.com/) |
| AutoGen (Microsoft) | 2023+ | [AutoGen](https://microsoft.github.io/autogen/) |

### Prompt-injection detection / defense
| Name | Year | Link |
|------|------|------|
| PromptShield | 2025 | [arXiv 2501.15145](https://arxiv.org/abs/2501.15145) |
| DataSentinel | 2025 | [arXiv 2504.11358](https://arxiv.org/abs/2504.11358) |
| PromptSleuth | 2025 | [arXiv 2508.20890](https://arxiv.org/abs/2508.20890) |
| SecAlign | 2024 | [arXiv 2410.05451](https://arxiv.org/abs/2410.05451) |
| DefensiveTokens | 2024 | [arXiv 2411.00459](https://arxiv.org/abs/2411.00459) |
| PromptGuard | 2025 | [Nature Sci. Reports](https://www.nature.com/articles/s41598-025-31086-y) |
| Attention-based (Rennervate-style) | 2025 | [arXiv 2512.08417](https://arxiv.org/abs/2512.08417) |

### Indirect & multimodal prompt injection
| Name | Year | Link |
|------|------|------|
| CrossInject | 2025 | [arXiv 2504.14348](https://arxiv.org/abs/2504.14348) |
| Spotlighting | 2024 | [arXiv 2403.14720](https://arxiv.org/abs/2403.14720) |
| Multimodal PI survey | 2025 | [arXiv 2509.05883](https://arxiv.org/abs/2509.05883) |
| External content injection | 2023 | [arXiv 2312.14197](https://arxiv.org/abs/2312.14197) |

### Text watermarking / content protection
| Name | Year | Link |
|------|------|------|
| Black-box watermark detection | 2024/25 | [arXiv 2405.20777](https://arxiv.org/abs/2405.20777) |
| Water-Probe / Water-Bag | 2024 (ICLR 2025) | [arXiv 2410.03168](https://arxiv.org/abs/2410.03168) |
| PostMark (EMNLP 2024) | 2024 | [arXiv 2406.14517](https://arxiv.org/abs/2406.14517) |
| Publicly-detectable watermarking | 2023 | [arXiv 2310.18491](https://arxiv.org/abs/2310.18491) |
| Radioactivity (NeurIPS 2024) | 2024 | [arXiv 2402.14904](https://arxiv.org/abs/2402.14904) |

### Memory / long-context
| Name | Year | Link |
|------|------|------|
| M+ (MemoryLLM extension) | 2025 | [arXiv 2502.00592](https://arxiv.org/abs/2502.00592) |
| LWM (Large World Model) | 2024 | [arXiv 2402.08268](https://arxiv.org/abs/2402.08268) |
| Samba | 2024 | [arXiv 2406.07522](https://arxiv.org/abs/2406.07522) |
| EpMAN | 2025 | [arXiv 2502.14280](https://arxiv.org/abs/2502.14280) |
| InfLLM | 2024 | [arXiv 2407.12117](https://arxiv.org/abs/2407.12117) |
| SELF-PARAM | 2024 | [arXiv 2410.00487](https://arxiv.org/abs/2410.00487) |
| MEMO (NeurIPS 2024) | 2024 | (NeurIPS 2024 proceedings) |
| DMC (NeurIPS 2024) | 2024 | (NeurIPS 2024 proceedings) |

### Belief / uncertainty / calibration
| Name | Year | Link |
|------|------|------|
| Uncertainty survey (LLMs) | 2025 | [arXiv 2504.18346](https://arxiv.org/abs/2504.18346) |
| UniCR | 2025 | [arXiv 2509.01455](https://arxiv.org/abs/2509.01455) |
| Linguistic verbal uncertainty (LVU) | 2025 | (OpenReview) |
| IB-EDL | 2025 | [arXiv 2502.06351](https://arxiv.org/abs/2502.06351) |
| Hidden-layer uncertainty | 2024 | [arXiv 2404.15993](https://arxiv.org/abs/2404.15993) |

### LLM reasoning & agentic systems
| Name | Year | Link |
|------|------|------|
| Frontiers in LLM reasoning survey | 2025 | [arXiv 2504.09037](https://arxiv.org/abs/2504.09037), [llm-reasoning-ai.github.io](https://llm-reasoning-ai.github.io/) |
| ARTIST (Microsoft) | 2025 | [Microsoft Research](https://www.microsoft.com/en-us/research/), [Agentic Reasoning](https://paperswithcode.com/paper/agentic-reasoning-reasoning-llms-with-tools) |
| Learning-to-reason | 2024+ | (covered in survey 2504.09037) |

### RAG (retrieval-augmented generation)
| Name | Year | Link |
|------|------|------|
| RAG survey (architectures & robustness) | 2025 | [arXiv 2506.00054](https://arxiv.org/abs/2506.00054) |
| ImpRAG | 2025 | [arXiv 2506.02279](https://arxiv.org/abs/2506.02279) |
| GraphRAG | 2024+ | [arXiv 2501.00309](https://arxiv.org/abs/2501.00309), [arXiv 2408.08921](https://arxiv.org/abs/2408.08921) |
| RAG systematic review | 2025 | [arXiv 2508.06401](https://arxiv.org/abs/2508.06401) |

### Model Context Protocol & agent tooling
| Name | Year | Link |
|------|------|------|
| Anthropic advanced tool use | 2025 | [Advanced tool use](https://www.anthropic.com/engineering/advanced-tool-use) — Tool Search Tool, Programmatic Tool Calling, Tool Use Examples |
| Model Context Protocol (MCP) | 2024 | [modelcontextprotocol.io](https://modelcontextprotocol.io) |
| Anthropic + MCP (code execution) | 2024+ | [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) |
| OpenAI Agents + MCP | 2024+ | [OpenAI agents MCP](https://openai.github.io/openai-agents-python/mcp/) |

---

*This doc is for research and comparison only. Focus: 2022–2025; cutting-edge and larger recent changes. No endorsement; verify licenses and suitability before use.*
