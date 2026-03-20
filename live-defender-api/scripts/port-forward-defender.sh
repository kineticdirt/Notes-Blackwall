#!/usr/bin/env bash
# Port-forward Defender cache API to localhost DEFENDER_LOCAL_PORT (default 9999).
# Prefers DEFENDER_SVC if set; else first svc matching *defender*; else DEFENDER_POD; else first pod matching *defender*.
set -euo pipefail

NS="${DEFENDER_K8S_NAMESPACE:-user-abhinav}"
LOCAL="${DEFENDER_LOCAL_PORT:-9999}"
REMOTE="${DEFENDER_REMOTE_PORT:-9999}"

pick_svc() {
  if [[ -n "${DEFENDER_SVC:-}" ]]; then
    echo "$DEFENDER_SVC"
    return
  fi
  kubectl get svc -n "$NS" -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null | grep -i defender | head -1 || true
}

pick_pod() {
  if [[ -n "${DEFENDER_POD:-}" ]]; then
    echo "$DEFENDER_POD"
    return
  fi
  kubectl get pods -n "$NS" -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}' 2>/dev/null | grep -i defender | head -1 || true
}

SVC="$(pick_svc)"
if [[ -n "$SVC" ]]; then
  echo "Port-forward service/$SVC $LOCAL:$REMOTE in namespace $NS"
  exec kubectl port-forward "svc/$SVC" "$LOCAL:$REMOTE" -n "$NS"
fi

POD="$(pick_pod)"
if [[ -n "$POD" ]]; then
  echo "Port-forward pod/$POD $LOCAL:$REMOTE in namespace $NS"
  exec kubectl port-forward "pod/$POD" "$LOCAL:$REMOTE" -n "$NS"
fi

echo "No defender svc/pod found in $NS. Set DEFENDER_SVC or DEFENDER_POD, or run list-defender-workloads.sh" >&2
exit 1
