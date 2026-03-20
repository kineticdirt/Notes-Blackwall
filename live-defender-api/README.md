# Live Defender `__cq` API — local runbook

Use this when the **real** Defender process is in Kubernetes and you want **`localhost:9999`** (via port-forward) for curl, MCP (`DEFENDER_BASE_URL`), or MvM.

**No cluster:** replay the same HTTP shapes from a CLI transcript with **`cterm-mock/`** (reads repo-root `def-cterm.txt`, serves `/__cq/cache/*` on port 9999). [httpbin.org](https://httpbin.org/) is not suitable for fixed mitigator JSON.

> **Cursor / agents cannot open k9s or use your kubeconfig.** Run every command below on **your Mac** (VPN on, `kubectl` working). If OIDC fails, fix network/auth first—nothing here can substitute for that.

## Prereqs

- `kubectl` context points at the right cluster (e.g. `eng3`).
- You can complete: `kubectl get ns` (no `get-token` / OIDC errors).
- Namespace that holds Defender (examples: `user-abhinav`, `user-ramesh`).

## Quick path (recommended)

**1. Pick namespace**

```bash
export DEFENDER_K8S_NAMESPACE=user-abhinav
```

**2. See what’s running**

```bash
bash live-defender-api/scripts/list-defender-workloads.sh
```

**3. Port-forward** — prefer a **Service** if one exists for Defender on port 9999:

```bash
bash live-defender-api/scripts/port-forward-defender.sh
```

Override if needed:

```bash
DEFENDER_K8S_NAMESPACE=user-ramesh \
DEFENDER_LOCAL_PORT=9999 \
DEFENDER_REMOTE_PORT=9999 \
bash live-defender-api/scripts/port-forward-defender.sh
```

If the script can’t find a Service, set **pod name** explicitly:

```bash
DEFENDER_K8S_NAMESPACE=user-ramesh \
DEFENDER_POD=defender-xxxx-xxxxx \
bash live-defender-api/scripts/port-forward-defender.sh
```

**4. Smoke test** (another terminal, repo root or anywhere):

```bash
bash live-defender-api/scripts/smoke-cache-api.sh
```

## k9s (manual)

If you prefer the TUI: `k9s` → select namespace (`:ns`) → `:pods` → find **defender** → note the **current** pod name (it changes after restarts). Port-forward can also be triggered from k9s depending on your k9s version/plugins; the shell script is the reproducible path.

## After the API is up

| Goal | Where |
|------|--------|
| Env for evals | `export DEFENDER_BASE_URL=http://127.0.0.1:9999` |
| MCP proxy (local) | `DEFENDER_MCP_URL`, see `retrieval-eval/experiments/README-DEFENDER-QWEN4B.md` |
| MvM runner | `python3 experiments/mvm_defender_api_runner.py` from `retrieval-eval/` |

## Troubleshooting

| Symptom | Likely cause |
|---------|----------------|
| `connection refused` to OIDC issuer | VPN / route / IdP; fix before `kubectl`. |
| `lost connection to pod` | Pod restarted; re-run port-forward to **new** pod or use **Service**. |
| `pods "…" not found` | Stale pod name; run `list-defender-workloads.sh` again. |
| `curl` “binary output” on `/__cq/help` | Non-JSON body; use `/__cq/cache/help` and `curl -s \| jq .`. |

## Files

| File | Purpose |
|------|--------|
| `scripts/list-defender-workloads.sh` | Pods + services matching `defender` in `$DEFENDER_K8S_NAMESPACE` |
| `scripts/port-forward-defender.sh` | Stable port-forward (service → pod fallback) |
| `scripts/smoke-cache-api.sh` | HTTP checks against `DEFENDER_BASE_URL` |
