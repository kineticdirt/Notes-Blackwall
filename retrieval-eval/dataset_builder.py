"""
Build a single source of truth dataset for retrieval eval: all permutations of
(eval_type, question_index, gravity, needle_position) plus optional multi-needle
combination cases. Used for both Elasticsearch ingest and RAG (Store / GraphQL / thinking).
"""
from __future__ import annotations
import hashlib
import json
import random
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple

if TYPE_CHECKING:
    from store import Store

from evals import (
    ASSISTANCE_WORK_QUESTIONS,
    EXPLANATION_WORK_QUESTIONS,
    NEEDLE_WORK_QUESTIONS,
    REASONING_WORK_QUESTIONS,
    EvalQuestion,
)
from needle import NEEDLE_POSITIONS, get_sentences, build_haystack, build_haystack_multi, chunk_text, get_haystack_length
from permutations import GRAVITIES

DATASET_NAME = "work"


@dataclass
class SingleCase:
    """One eval case: one needle, one query, one haystack config."""
    case_id: str
    doc_id: str
    eval_type: str
    question_index: int
    gravity: str
    needle_position: str
    needle: str
    query: str
    primary: str
    markers: List[str]
    seed: int  # for reproducible haystack build

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CombinationCase:
    """Multi-needle case: same haystack, multiple (needle, query) pairs to test interference."""
    case_id: str
    doc_id: str
    gravity: str
    needles: List[Tuple[str, str, str, List[str]]]  # (needle, query, primary, markers) per target
    positions: List[str]  # one per needle, from NEEDLE_POSITIONS
    seed: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "case_id": self.case_id,
            "doc_id": self.doc_id,
            "gravity": self.gravity,
            "needles": [
                {"needle": n, "query": q, "primary": p, "markers": m}
                for n, q, p, m in self.needles
            ],
            "positions": list(self.positions),
            "seed": self.seed,
        }


def _work_questions_by_type() -> Dict[str, List[EvalQuestion]]:
    return {
        "needle": NEEDLE_WORK_QUESTIONS,
        "reasoning": REASONING_WORK_QUESTIONS,
        "explanation": EXPLANATION_WORK_QUESTIONS,
        "assistance": ASSISTANCE_WORK_QUESTIONS,
    }


def _seed_for_case(case_id: str) -> int:
    return int(hashlib.sha256(case_id.encode()).hexdigest()[:8], 16) % (2**31)


def all_single_cases() -> List[SingleCase]:
    """All single-needle cases: eval_type × question_index × gravity × needle_position."""
    cases: List[SingleCase] = []
    by_type = _work_questions_by_type()
    for eval_type, questions in by_type.items():
        for q_idx, q in enumerate(questions):
            for gravity in GRAVITIES:
                for pos in NEEDLE_POSITIONS:
                    case_id = f"work_{eval_type}_{q_idx}_{gravity}_{pos}"
                    doc_id = f"doc_{case_id}"
                    seed = _seed_for_case(case_id)
                    cases.append(
                        SingleCase(
                            case_id=case_id,
                            doc_id=doc_id,
                            eval_type=eval_type,
                            question_index=q_idx,
                            gravity=gravity,
                            needle_position=pos,
                            needle=q.needle,
                            query=q.query,
                            primary=q.primary,
                            markers=list(q.markers),
                            seed=seed,
                        )
                    )
    return cases


def all_combination_cases(
    max_pairs: Optional[int] = None,
    same_type_only: bool = False,
) -> List[CombinationCase]:
    """
    Multi-needle cases: two needles in one haystack to test "does one cause another to be worse".
    Pairs are (q1, q2) from the question bank; we inject both and can query for either.
    """
    by_type = _work_questions_by_type()
    flat: List[Tuple[str, int, EvalQuestion]] = []
    for et, questions in by_type.items():
        for qi, q in enumerate(questions):
            flat.append((et, qi, q))
    pairs: List[Tuple[Tuple[str, int, EvalQuestion], Tuple[str, int, EvalQuestion]]] = []
    for i in range(len(flat)):
        for j in range(i + 1, len(flat)):
            if same_type_only and flat[i][0] != flat[j][0]:
                continue
            pairs.append((flat[i], flat[j]))
    if max_pairs is not None:
        pairs = pairs[:max_pairs]
    cases: List[CombinationCase] = []
    positions = list(NEEDLE_POSITIONS)
    for (et1, qi1, q1), (et2, qi2, q2) in pairs:
        for gravity in GRAVITIES:
            case_id = f"comb_{et1}_{qi1}_{et2}_{qi2}_{gravity}"
            doc_id = f"doc_{case_id}"
            seed = _seed_for_case(case_id)
            needles_payload = [
                (q1.needle, q1.query, q1.primary, list(q1.markers)),
                (q2.needle, q2.query, q2.primary, list(q2.markers)),
            ]
            pos_assign = [positions[0], positions[1]] if len(positions) >= 2 else ["middle", "middle"]
            cases.append(
                CombinationCase(
                    case_id=case_id,
                    doc_id=doc_id,
                    gravity=gravity,
                    needles=needles_payload,
                    positions=pos_assign,
                    seed=seed,
                )
            )
    return cases


def build_haystack_for_case(case: SingleCase) -> Tuple[str, List[str], int]:
    """
    Build haystack text and chunks for a SingleCase (reproducible via seed).
    Returns (full_text, chunks, sentence_index_where_needle).
    """
    sentences = get_sentences(DATASET_NAME)
    rng = random.Random(case.seed)
    length = get_haystack_length(case.gravity)
    out: List[str] = []
    for _ in range(length):
        out.append(rng.choice(sentences))
    idx = {"start": 0, "middle": length // 2, "end": length - 1}.get(case.needle_position, length // 2)
    out[idx] = case.needle
    text = " ".join(out)
    chunks = chunk_text(text)
    needle_chunk_idx = -1
    for i, c in enumerate(chunks):
        if case.needle in c:
            needle_chunk_idx = i
            break
    return text, chunks, needle_chunk_idx


def build_haystack_for_combination_case(case: CombinationCase) -> Tuple[str, List[str], List[int]]:
    """
    Build haystack with multiple needles (reproducible via seed).
    Returns (full_text, chunks, chunk_indices where each needle appears).
    """
    sentences = get_sentences(DATASET_NAME)
    rng = random.Random(case.seed)
    needles_with_pos = [(n[0], pos) for n, pos in zip(case.needles, case.positions)]
    text, _sent_indices = build_haystack_multi(case.gravity, needles_with_pos, sentences, rng)
    chunks = chunk_text(text)
    chunk_indices: List[int] = []
    for needle_text, _, _, _ in case.needles:
        found = -1
        for i, c in enumerate(chunks):
            if needle_text in c:
                found = i
                break
        chunk_indices.append(found)
    return text, chunks, chunk_indices


def write_dataset_json(
    path: Path,
    single_cases: Optional[List[SingleCase]] = None,
    combination_cases: Optional[List[CombinationCase]] = None,
) -> None:
    """Write dataset manifest (cases) to JSON for runner and ES metadata."""
    single_cases = single_cases if single_cases is not None else all_single_cases()
    combination_cases = combination_cases if combination_cases is not None else []
    payload = {
        "dataset": DATASET_NAME,
        "single_cases": [c.to_dict() for c in single_cases],
        "combination_cases": [c.to_dict() for c in combination_cases],
        "count_single": len(single_cases),
        "count_combination": len(combination_cases),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))


def write_corpus_jsonl(
    path: Path,
    single_cases: Optional[List[SingleCase]] = None,
    combination_cases: Optional[List[CombinationCase]] = None,
) -> int:
    """
    Materialize haystacks for all single (and optionally combination) cases and write
    one JSONL line per chunk. Each line: { doc_id, chunk_index, text, case_id, eval_type? }.
    Returns total number of chunks written.
    Used for Elasticsearch bulk index and for RAG Store ingest.
    """
    single_cases = single_cases if single_cases is not None else all_single_cases()
    combination_cases = combination_cases if combination_cases is not None else []
    path.parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with open(path, "w") as f:
        for case in single_cases:
            _, chunks, _ = build_haystack_for_case(case)
            for i, text in enumerate(chunks):
                line = {
                    "doc_id": case.doc_id,
                    "chunk_index": i,
                    "text": text,
                    "case_id": case.case_id,
                    "eval_type": case.eval_type,
                    "gravity": case.gravity,
                }
                f.write(json.dumps(line) + "\n")
                total += 1
        for case in combination_cases:
            _, chunks, _ = build_haystack_for_combination_case(case)
            for i, text in enumerate(chunks):
                line = {
                    "doc_id": case.doc_id,
                    "chunk_index": i,
                    "text": text,
                    "case_id": case.case_id,
                    "gravity": case.gravity,
                }
                f.write(json.dumps(line) + "\n")
                total += 1
    return total


def load_dataset_json(path: Path) -> Tuple[List[Dict], List[Dict]]:
    """Load dataset manifest; return (single_cases dicts, combination_cases dicts)."""
    data = json.loads(path.read_text())
    return data.get("single_cases", []), data.get("combination_cases", [])


def load_corpus_chunks_for_doc(corpus_path: Path, doc_id: str) -> List[str]:
    """Read corpus JSONL and return list of chunk texts for the given doc_id (order by chunk_index)."""
    chunks_by_idx: Dict[int, str] = {}
    with open(corpus_path) as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("doc_id") != doc_id:
                continue
            chunks_by_idx[row["chunk_index"]] = row["text"]
    return [chunks_by_idx[i] for i in sorted(chunks_by_idx)]


def ingest_corpus_doc_to_store(store: Store, corpus_path: Path, doc_id: str) -> List[str]:
    """Load chunks for doc_id from corpus JSONL and ingest into Store. Returns chunk node ids."""
    chunks = load_corpus_chunks_for_doc(corpus_path, doc_id)
    return store.ingest_chunks(chunks, doc_id=doc_id)
