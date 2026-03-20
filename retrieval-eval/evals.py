"""
Eval types: needle, reasoning, explanation, assistance.
Each defines query, injected content, and success criterion for a dataset.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class EvalQuestion:
    needle: str
    query: str
    primary: str
    markers: List[str]


# Default (generic) and cequence_cs share sentence sets from needle.py; we only define per-type needles/queries here.

# ---- NEEDLE ----
NEEDLE_DEFAULT = "The secret code for this eval is NEEDLE-42."
NEEDLE_QUERY_DEFAULT = "What is the secret code?"
NEEDLE_MARKER_DEFAULT = "NEEDLE-42"

NEEDLE_CEQUENCE = "The Cequence BlackWall retrieval eval passphrase is NEEDLE-CS-42."
NEEDLE_QUERY_CEQUENCE = "What is the Cequence BlackWall retrieval eval passphrase?"
NEEDLE_MARKER_CEQUENCE = "NEEDLE-CS-42"

NEEDLE_CEQUENCE_QUESTIONS: List[EvalQuestion] = [
    EvalQuestion(
        needle="The Cequence BlackWall retrieval eval passphrase is NEEDLE-CS-42.",
        query="What is the Cequence BlackWall retrieval eval passphrase?",
        primary="NEEDLE-CS-42",
        markers=["NEEDLE-CS-42"],
    ),
    EvalQuestion(
        needle="The only outbound header source type that must not have a prefix set is access_key.",
        query="What is the only outbound header source type that must not have a prefix set, and why?",
        primary="access_key",
        markers=["access_key", "prefix"],
    ),
    EvalQuestion(
        needle="The pipeline order in the assistant manifest is: prompt_injection_gate, MCP, workflow_canvas, subagents.",
        query="What is the exact pipeline order in the assistant manifest? List the four stages.",
        primary="pipeline_order",
        markers=["prompt_injection_gate", "MCP", "workflow_canvas", "subagents"],
    ),
]

# ---- REASONING (multi-step from context) ----
REASONING_CEQUENCE = (
    "The Cequence assistant pipeline order is: prompt_injection_gate, then MCP, then workflow_canvas, then subagents."
)
REASONING_QUERY_CEQUENCE = (
    "What is the Cequence assistant pipeline order? Reason step-by-step from the context and state the order."
)
# Success: answer should contain at least one of these (reasoning used context)
REASONING_MARKERS_CEQUENCE = ["pipeline", "gate", "MCP", "workflow", "subagents", "prompt_injection"]

REASONING_CEQUENCE_QUESTIONS: List[EvalQuestion] = [
    EvalQuestion(
        needle="The Cequence assistant pipeline order is: prompt_injection_gate, then MCP, then workflow_canvas, then subagents.",
        query="What is the Cequence assistant pipeline order? Reason step-by-step from the context and state the order.",
        primary="reasoning",
        markers=["pipeline", "gate", "MCP", "workflow", "subagents", "prompt_injection"],
    ),
    EvalQuestion(
        needle="Validation rejects at API when required fields are missing; gateway returns 401 when JWT is invalid or missing at request time.",
        query="When do we get 400 from the API vs 401 from the gateway? Give one example of each and reason from the context.",
        primary="reasoning",
        markers=["400", "401", "API", "gateway", "validation", "JWT"],
    ),
    EvalQuestion(
        needle="Forward Inbound Header forbids authorization and cookie as source headers to avoid leaking credentials or session to upstream.",
        query="Why does Forward Inbound Header forbid using authorization or cookie as the source header? Reason from the context.",
        primary="reasoning",
        markers=["authorization", "cookie", "forbid", "credential", "security", "upstream"],
    ),
]

REASONING_DEFAULT = "The correct sequence for deployment is: build, test, then deploy."
REASONING_QUERY_DEFAULT = "What is the correct sequence for deployment? Reason step-by-step from the context."
REASONING_MARKERS_DEFAULT = ["build", "test", "deploy", "sequence"]

# ---- EXPLANATION (explain a concept from context) ----
EXPLANATION_CEQUENCE = (
    "Hybrid search in this eval combines substring and vector retrieval with Reciprocal Rank Fusion (RRF)."
)
EXPLANATION_QUERY_CEQUENCE = "Explain how hybrid search works in this eval, based only on the context."
EXPLANATION_MARKERS_CEQUENCE = ["RRF", "vector", "substring", "hybrid", "fusion", "reciprocal"]

EXPLANATION_CEQUENCE_QUESTIONS: List[EvalQuestion] = [
    EvalQuestion(
        needle="Hybrid search in this eval combines substring and vector retrieval with Reciprocal Rank Fusion (RRF).",
        query="Explain how hybrid search works in this eval, based only on the context.",
        primary="explanation",
        markers=["RRF", "vector", "substring", "hybrid", "fusion", "reciprocal"],
    ),
    EvalQuestion(
        needle="access_key outbound headers cannot have a prefix because the key is sent as-is; a prefix would break the signing or auth scheme.",
        query="Explain why access_key outbound headers cannot have a prefix. What would go wrong if we allowed it?",
        primary="explanation",
        markers=["access_key", "prefix", "signing", "auth", "key"],
    ),
    EvalQuestion(
        needle="OAuth2 Service Account uses a single service token; On Behalf of User uses token exchange with the caller's token. Use Service Account for machine-to-machine; use On Behalf of User when the upstream must see the user identity.",
        query="What is the difference between OAuth2 Service Account and On Behalf of User for outbound headers? When would you use each?",
        primary="explanation",
        markers=["Service Account", "On Behalf", "token exchange", "user identity", "machine-to-machine"],
    ),
]

EXPLANATION_DEFAULT = "Rate limiting protects backends by capping request volume per client."
EXPLANATION_QUERY_DEFAULT = "Explain how rate limiting protects backends, based on the context."
EXPLANATION_MARKERS_DEFAULT = ["rate", "limit", "backend", "request", "cap"]

# ---- WORK DATASET (Jira + Confluence only; no BlackWall/local) ----
# Expanded from WORK_EVAL_PROJECTS_AND_PRODUCTS.md to hit all projects/products and criteria.
NEEDLE_WORK_QUESTIONS: List[EvalQuestion] = [
    EvalQuestion(
        needle="The Jira project key for API Fury is AF.",
        query="What is the Jira project key for API Fury?",
        primary="AF",
        markers=["AF"],
    ),
    EvalQuestion(
        needle="The only outbound header source type that must not have a prefix set is access_key.",
        query="What is the only outbound header source type that must not have a prefix set, and why?",
        primary="access_key",
        markers=["access_key", "prefix"],
    ),
    EvalQuestion(
        needle="The Confluence space key for Product Management is PM; the space key for CQ - API Security is API.",
        query="What are the Confluence space keys for Product Management and for CQ - API Security?",
        primary="PM_API",
        markers=["PM", "API"],
    ),
    EvalQuestion(
        needle="The Jira project key for Armor is AR.",
        query="What is the Jira project key for Armor?",
        primary="AR",
        markers=["AR"],
    ),
    EvalQuestion(
        needle="The Jira project key for API Test Cases is ATC; for CQAI Efficacy Engineering it is CEE.",
        query="What are the Jira project keys for API Test Cases and for CQAI Efficacy Engineering?",
        primary="ATC_CEE",
        markers=["ATC", "CEE"],
    ),
    EvalQuestion(
        needle="The Confluence space key for Stealth SUPPORT is SS; for Velocity Manager 0.1 it is VM; for Proof Of Value it is POV.",
        query="What are the Confluence space keys for Stealth SUPPORT, Velocity Manager 0.1, and Proof Of Value?",
        primary="SS_VM_POV",
        markers=["SS", "VM", "POV"],
    ),
    EvalQuestion(
        needle="The Jira project key for Defender is DEF; for Platform it is PLAT.",
        query="What is the Jira project key for Defender? For Platform?",
        primary="DEF_PLAT",
        markers=["DEF", "PLAT"],
    ),
]

REASONING_WORK_QUESTIONS: List[EvalQuestion] = [
    EvalQuestion(
        needle="Validation rejects at API when required fields are missing; gateway returns 401 when JWT is invalid or missing at request time.",
        query="When do we get 400 from the API vs 401 from the gateway? Give one example of each and reason from the context.",
        primary="reasoning",
        markers=["400", "401", "API", "gateway", "validation", "JWT"],
    ),
    EvalQuestion(
        needle="Forward Inbound Header forbids authorization and cookie as source headers to avoid leaking credentials or session to upstream.",
        query="Why does Forward Inbound Header forbid using authorization or cookie as the source header? Reason from the context.",
        primary="reasoning",
        markers=["authorization", "cookie", "forbid", "credential", "security", "upstream"],
    ),
    EvalQuestion(
        needle="Jira project ASJCI supports issue types Task, Bug, Story, Epic, and Subtask.",
        query="Which issue types does the API Security JIRA Connector Integration project support? List them from the context.",
        primary="reasoning",
        markers=["Task", "Bug", "Story", "Epic", "Subtask", "ASJCI"],
    ),
    EvalQuestion(
        needle="Projects AF and AR support only Task and Sub-task; project ASJCI supports Task, Bug, Story, Epic, and Subtask.",
        query="Which Jira projects support only Task and Sub-task, and which support the full set including Bug, Story, and Epic? Reason from the context.",
        primary="reasoning",
        markers=["AF", "AR", "ASJCI", "Task", "Epic", "Bug", "Story"],
    ),
    EvalQuestion(
        needle="CQ-Service Desk space key is CSD; CQ - Service Desk 2 is CSD2. Both are used for service desk documentation.",
        query="What are the Confluence space keys for the two CQ Service Desk spaces? Reason from the context.",
        primary="reasoning",
        markers=["CSD", "CSD2", "Service Desk"],
    ),
]

EXPLANATION_WORK_QUESTIONS: List[EvalQuestion] = [
    EvalQuestion(
        needle="access_key outbound headers cannot have a prefix because the key is sent as-is; a prefix would break the signing or auth scheme.",
        query="Explain why access_key outbound headers cannot have a prefix. What would go wrong if we allowed it?",
        primary="explanation",
        markers=["access_key", "prefix", "signing", "auth", "key"],
    ),
    EvalQuestion(
        needle="OAuth2 Service Account uses a single service token; On Behalf of User uses token exchange with the caller's token. Use Service Account for machine-to-machine; use On Behalf of User when the upstream must see the user identity.",
        query="What is the difference between OAuth2 Service Account and On Behalf of User for outbound headers? When would you use each?",
        primary="explanation",
        markers=["Service Account", "On Behalf", "token exchange", "user identity", "machine-to-machine"],
    ),
    EvalQuestion(
        needle="Velocity Manager installs Splunk universal forwarder in the Docker image; export config is under data-export and alert data goes to analysis and mitigation subfolders.",
        query="Explain how Velocity Manager exports data to Splunk. Where is the forwarder and where is the export config?",
        primary="explanation",
        markers=["Splunk", "forwarder", "data-export", "analysis", "mitigation"],
    ),
    EvalQuestion(
        needle="Digital Skimming (Magecart) Protection documentation lives in Confluence space DSMP; API Security docs are in space API.",
        query="Where is Digital Skimming Protection documented, and where is API Security documentation? Explain from the context.",
        primary="explanation",
        markers=["DSMP", "API", "Confluence", "documentation"],
    ),
]

ASSISTANCE_WORK_QUESTIONS: List[EvalQuestion] = [
    EvalQuestion(
        needle="To export data to Splunk from Velocity Manager: install the .spl license in the Docker image, restart the Splunk forwarder, add a monitor for the data-export data folder, then configure export for analysis or mitigation in the UI.",
        query="How do I export Velocity Manager detection data to Splunk? Give exact steps from the context.",
        primary="assistance",
        markers=["Splunk", "forwarder", "data-export", "monitor", "UI"],
    ),
    EvalQuestion(
        needle="To find API Security documentation, use Confluence space API; for Product Management use space PM; for Xangent product docs use space XAN.",
        query="Where do I find API Security documentation and Product Management content in Confluence? Give space keys from the context.",
        primary="assistance",
        markers=["API", "PM", "XAN", "Confluence", "space"],
    ),
]

# ---- ASSISTANCE (legacy cequence_cs) ----
ASSISTANCE_CEQUENCE = (
    "To run the retrieval eval for Cequence, use: python3 run_sequential.py --dataset cequence_cs from the retrieval-eval directory."
)
ASSISTANCE_QUERY_CEQUENCE = "How do I run the retrieval eval for the Cequence dataset? Give exact steps from the context."
ASSISTANCE_MARKERS_CEQUENCE = ["run_sequential", "cequence_cs", "retrieval-eval", "dataset"]

ASSISTANCE_DEFAULT = "To run tests, execute: pytest tests/ from the project root."
ASSISTANCE_QUERY_DEFAULT = "How do I run tests from the project root? Give exact steps from the context."
ASSISTANCE_MARKERS_DEFAULT = ["pytest", "tests", "project root"]


def get_question_count(dataset: str, eval_type: str) -> int:
    """Return number of questions for this dataset and eval_type (1 when no question bank)."""
    if dataset == "work":
        if eval_type == "needle":
            return len(NEEDLE_WORK_QUESTIONS)
        if eval_type == "reasoning":
            return len(REASONING_WORK_QUESTIONS)
        if eval_type == "explanation":
            return len(EXPLANATION_WORK_QUESTIONS)
        if eval_type == "assistance":
            return len(ASSISTANCE_WORK_QUESTIONS)
    if dataset == "cequence_cs" and eval_type in ("needle", "reasoning", "explanation"):
        if eval_type == "needle":
            return len(NEEDLE_CEQUENCE_QUESTIONS)
        if eval_type == "reasoning":
            return len(REASONING_CEQUENCE_QUESTIONS)
        if eval_type == "explanation":
            return len(EXPLANATION_CEQUENCE_QUESTIONS)
    return 1


def get_test_config(
    dataset: str,
    eval_type: str,
    question_index: int = 0,
) -> Tuple[str, str, str, List[str]]:
    """
    Return (needle_sentence, query, answer_marker_or_primary, success_markers).
    For needle, success_markers is single-item list; for others, any match = pass.
    For cequence_cs needle/reasoning/explanation, question_index selects from the question bank (clamped).
    """
    if dataset == "work":
        if eval_type == "needle":
            lst = NEEDLE_WORK_QUESTIONS
            idx = max(0, min(question_index, len(lst) - 1))
            q = lst[idx]
            return (q.needle, q.query, q.primary, q.markers)
        if eval_type == "reasoning":
            lst = REASONING_WORK_QUESTIONS
            idx = max(0, min(question_index, len(lst) - 1))
            q = lst[idx]
            return (q.needle, q.query, q.primary, q.markers)
        if eval_type == "explanation":
            lst = EXPLANATION_WORK_QUESTIONS
            idx = max(0, min(question_index, len(lst) - 1))
            q = lst[idx]
            return (q.needle, q.query, q.primary, q.markers)
        if eval_type == "assistance":
            lst = ASSISTANCE_WORK_QUESTIONS
            idx = max(0, min(question_index, len(lst) - 1))
            q = lst[idx]
            return (q.needle, q.query, q.primary, q.markers)
    if dataset == "cequence_cs":
        if eval_type == "needle":
            lst = NEEDLE_CEQUENCE_QUESTIONS
            idx = max(0, min(question_index, len(lst) - 1))
            q = lst[idx]
            return (q.needle, q.query, q.primary, q.markers)
        if eval_type == "reasoning":
            lst = REASONING_CEQUENCE_QUESTIONS
            idx = max(0, min(question_index, len(lst) - 1))
            q = lst[idx]
            return (q.needle, q.query, q.primary, q.markers)
        if eval_type == "explanation":
            lst = EXPLANATION_CEQUENCE_QUESTIONS
            idx = max(0, min(question_index, len(lst) - 1))
            q = lst[idx]
            return (q.needle, q.query, q.primary, q.markers)
        if eval_type == "assistance":
            return (ASSISTANCE_CEQUENCE, ASSISTANCE_QUERY_CEQUENCE, "assistance", ASSISTANCE_MARKERS_CEQUENCE)
    # default
    if eval_type == "needle":
        return (NEEDLE_DEFAULT, NEEDLE_QUERY_DEFAULT, NEEDLE_MARKER_DEFAULT, [NEEDLE_MARKER_DEFAULT])
    if eval_type == "reasoning":
        return (REASONING_DEFAULT, REASONING_QUERY_DEFAULT, "reasoning", REASONING_MARKERS_DEFAULT)
    if eval_type == "explanation":
        return (EXPLANATION_DEFAULT, EXPLANATION_QUERY_DEFAULT, "explanation", EXPLANATION_MARKERS_DEFAULT)
    if eval_type == "assistance":
        return (ASSISTANCE_DEFAULT, ASSISTANCE_QUERY_DEFAULT, "assistance", ASSISTANCE_MARKERS_DEFAULT)
    raise ValueError(f"unknown eval_type={eval_type!r} dataset={dataset!r}")


def is_answer_correct(answer: str, success_markers: List[str]) -> bool:
    """True if answer contains any of the success markers (case-insensitive)."""
    if not answer or answer.startswith("(error:") or answer.startswith("(no answer)"):
        return False
    low = answer.lower()
    return any(m.lower() in low for m in success_markers)
