#!/usr/bin/env bash
# Validate assistant manifest.yaml. No Python. Security: no secrets; pipeline consistency.
# Usage: ./assistant/validate.sh [path/to/manifest.yaml]
# Exit 0 = valid; non-zero = invalid (errors to stderr).

MANIFEST="${1:-$(dirname "$0")/manifest.yaml}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ERR=0

# Required top-level keys
require_key() {
  if ! grep -q "^${1}:" "$MANIFEST" 2>/dev/null; then
    echo "validation error: missing required key: ${1}" >&2
    ERR=1
  fi
}

require_key "version"
require_key "name"
require_key "consistency"
require_key "orchestrators"

# Consistency sub-keys
if grep -q "^consistency:" "$MANIFEST"; then
  if ! grep -A5 "^consistency:" "$MANIFEST" | grep -q "pipeline_order"; then
    echo "validation error: consistency.pipeline_order missing" >&2
    ERR=1
  fi
  if ! grep -A10 "^consistency:" "$MANIFEST" | grep -q "secrets"; then
    echo "validation error: consistency.secrets missing" >&2
    ERR=1
  fi
  if ! grep -A10 "^consistency:" "$MANIFEST" | grep -q "audit_sink"; then
    echo "validation error: consistency.audit_sink missing" >&2
    ERR=1
  fi
fi

# Pipeline order entries must exist as orchestrator ids (simple check: orchestrators section contains each id)
for id in prompt_injection_gate mcp workflow_canvas subagents; do
  if ! grep -q "^  ${id}:" "$MANIFEST" 2>/dev/null; then
    echo "validation warning: pipeline orchestrator not defined: ${id}" >&2
  fi
done

# Forbid secret-like values in manifest (heuristic: key names that suggest secrets, with non-placeholder value)
if grep -E "^\s*(api_key|password|secret|token|credential):\s*[^#\s].*[a-zA-Z0-9]{20,}" "$MANIFEST" 2>/dev/null; then
  echo "validation error: manifest must not contain secret values (use env or vault)" >&2
  ERR=1
fi
# Placeholder-only is ok
if grep -E "^\s*(api_key|password|secret):\s*\$\{" "$MANIFEST" 2>/dev/null; then
  : # env ref like ${VAR} is allowed
fi

if [ "$ERR" -eq 0 ]; then
  echo "manifest valid: $MANIFEST" >&2
fi
exit "$ERR"
