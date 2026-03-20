"""
Bulk ingest corpus_work.jsonl into Elasticsearch for retrieval eval.
Index name: retrieval_eval_work. Each chunk is one document with doc_id, chunk_index, text, case_id, eval_type, gravity.
Requires: pip install elasticsearch
Usage:
  export ELASTICSEARCH_URL=http://localhost:9200
  python3 ingest_elasticsearch.py [--index retrieval_eval_work] [--corpus results/corpus_work.jsonl]
"""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path

def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk ingest corpus JSONL into Elasticsearch.")
    parser.add_argument("--index", default="retrieval_eval_work", help="Elasticsearch index name.")
    parser.add_argument("--corpus", type=Path, default=None, help="Path to corpus_work.jsonl.")
    parser.add_argument("--url", default=None, help="Elasticsearch URL (default: ELASTICSEARCH_URL env).")
    args = parser.parse_args()

    try:
        from elasticsearch import Elasticsearch
    except ImportError:
        print("Install elasticsearch: pip install elasticsearch", file=sys.stderr)
        sys.exit(1)

    root = Path(__file__).resolve().parent
    corpus_path = args.corpus or (root / "results" / "corpus_work.jsonl")
    if not corpus_path.exists():
        print(f"Corpus not found: {corpus_path}. Run: python3 build_corpus.py", file=sys.stderr)
        sys.exit(1)

    url = args.url or os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
    es = Elasticsearch(url)
    index = args.index

    # Create index with mapping (optional: add dense_vector if you index embeddings later)
    mapping = {
        "mappings": {
            "properties": {
                "doc_id": {"type": "keyword"},
                "chunk_index": {"type": "integer"},
                "text": {"type": "text"},
                "case_id": {"type": "keyword"},
                "eval_type": {"type": "keyword"},
                "gravity": {"type": "keyword"},
            }
        }
    }
    try:
        es.indices.create(index=index, body=mapping)
        print(f"Created index {index}")
    except Exception as e:
        if "resource_already_exists" not in str(e).lower() and "already_exists" not in str(e).lower():
            raise
        print(f"Index {index} already exists")

    import json as _json
    bulk_actions = []
    count = 0
    with open(corpus_path) as f:
        for line in f:
            if not line.strip():
                continue
            doc = _json.loads(line)
            bulk_actions.append({"index": {"_index": index, "_id": f"{doc['doc_id']}_{doc['chunk_index']}"}})
            bulk_actions.append({k: doc.get(k) for k in ("doc_id", "chunk_index", "text", "case_id", "eval_type", "gravity") if doc.get(k) is not None})
            count += 1
            if len(bulk_actions) >= 500:
                es.bulk(body=bulk_actions, refresh=False)
                bulk_actions = []
                print(f"Indexed {count} chunks...")

    if bulk_actions:
        es.bulk(body=bulk_actions, refresh=True)
    print(f"Done. Indexed {count} chunks into {index}.")

if __name__ == "__main__":
    main()
