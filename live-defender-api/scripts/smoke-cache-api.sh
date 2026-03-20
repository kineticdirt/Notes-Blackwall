#!/usr/bin/env bash
# Smoke-test Defender __cq cache HTTP API on DEFENDER_BASE_URL (default http://127.0.0.1:9999).
set -euo pipefail

BASE="${DEFENDER_BASE_URL:-http://127.0.0.1:9999}"
BASE="${BASE%/}"

echo "GET $BASE/__cq/cache/help"
curl -sfS "$BASE/__cq/cache/help" | head -c 2000
echo ""
echo ""
echo "GET $BASE/__cq/cache/all (truncated)"
curl -sfS "$BASE/__cq/cache/all" | head -c 1500
echo ""
echo "OK"
