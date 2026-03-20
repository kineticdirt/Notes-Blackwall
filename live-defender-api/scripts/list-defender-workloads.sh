#!/usr/bin/env bash
# List defender-related pods and services in DEFENDER_K8S_NAMESPACE (default: user-abhinav).
set -euo pipefail

NS="${DEFENDER_K8S_NAMESPACE:-user-abhinav}"

echo "Namespace: $NS"
echo "=== pods (grep defender) ==="
kubectl get pods -n "$NS" -o wide 2>/dev/null | grep -i defender || echo "(no pod names matching 'defender')"
echo ""
echo "=== services (grep defender) ==="
kubectl get svc -n "$NS" 2>/dev/null | grep -i defender || echo "(no svc names matching 'defender')"
echo ""
echo "Tip: copy a CURRENT pod name or svc name for port-forward-defender.sh"
