"""Load API key from retrieval-eval/.api-key, .api-key.example, or ANTHROPIC_API_KEY env."""
from pathlib import Path

def load_api_key() -> str:
    """Single place: .api-key first, then .api-key.example, then env. Raises if missing."""
    root = Path(__file__).resolve().parent  # retrieval-eval/
    for name in (".api-key", ".api-key.example"):
        key_file = root / name
        if key_file.exists():
            raw = key_file.read_text()
            for line in raw.splitlines():
                key = line.strip()
                if key and not key.startswith("#") and not key.lower().startswith("paste") and len(key) > 20:
                    return key
    import os
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    raise RuntimeError(
        "No API key found. Paste your Claude API key in retrieval-eval/.api-key or .api-key.example (one line) "
        "or set ANTHROPIC_API_KEY. See retrieval-eval/README.md."
    )
