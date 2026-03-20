"""All permutation types and gravity levels. Sequential runner iterates over these."""
from dataclasses import dataclass
from typing import List

# Design permutations: RAG/retrieval strategies
SEARCH_TYPES = ("substring", "vector", "hybrid", "graph")
# Test types: how we evaluate model + retrieval
EVAL_TYPES = ("needle", "reasoning", "explanation", "assistance")
# Haystack size / difficulty (more levels = more combos)
GRAVITIES = ("tiny", "short", "medium", "long", "xlong")
# Retrieval depth (top-k passed to retriever and metrics)
K_VALUES = (3, 5, 10, 15, 20)
# Needle position in haystack (when building inline; corpus uses its own doc_id)
NEEDLE_POSITIONS = ("start", "middle", "end")
# Chunk size in words (when building haystack inline; prebuilt corpus has fixed size)
CHUNK_SIZES = (100, 200, 400)
# Dataset sources: internal (default, work, cequence_cs) + external (squad, squad_v2, boolq, race_middle)
DATASET_SOURCES = ("default", "work", "cequence_cs", "squad", "squad_v2", "boolq", "race_middle")


@dataclass
class Permutation:
    search_type: str      # substring | vector | hybrid | graph
    thinking: bool        # True = reason then answer, False = direct answer
    eval_type: str        # needle | reasoning | explanation | assistance
    gravity: str          # tiny | short | medium | long | xlong
    k: int = 5            # retrieval limit (top-k)
    needle_position: str = "middle"   # start | middle | end
    chunk_size: int = 200  # words per chunk when building haystack
    dataset_source: str = "default"   # which dataset to run on (internal or external)

    def design_id(self) -> str:
        """Unique design label: retrieval strategy + gravity + thinking + k + position + chunk + dataset."""
        base = f"{self.search_type}_{self.gravity}_k{self.k}_{self.needle_position}_c{self.chunk_size}_{self.dataset_source}"
        return f"{base}_thinking" if self.thinking else base


def all_permutations() -> List[Permutation]:
    """All permutations: search_type × thinking × gravity × eval_type × k × needle_position × chunk_size × dataset_source."""
    out: List[Permutation] = []
    for search in SEARCH_TYPES:
        for thinking in (False, True):
            for gravity in GRAVITIES:
                for eval_type in EVAL_TYPES:
                    for k in K_VALUES:
                        for needle_position in NEEDLE_POSITIONS:
                            for chunk_size in CHUNK_SIZES:
                                for dataset_source in DATASET_SOURCES:
                                    out.append(Permutation(
                                        search_type=search,
                                        thinking=thinking,
                                        eval_type=eval_type,
                                        gravity=gravity,
                                        k=k,
                                        needle_position=needle_position,
                                        chunk_size=chunk_size,
                                        dataset_source=dataset_source,
                                    ))
    return out
