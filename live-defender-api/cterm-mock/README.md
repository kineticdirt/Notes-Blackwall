# Mock Defender `__cq/cache` API from `def-cterm.txt`

[**httpbin.org**](https://httpbin.org/) is for **request/response introspection** (`/get`, `/post`, `/headers`, …). It does **not** let you host arbitrary static JSON at `/__cq/cache/info` etc., so this app **replays** the mitigator CLI transcript instead.

## Run (port 9999, same as live Defender)

From repo root or this directory:

```bash
cd live-defender-api/cterm-mock
pip install -r requirements.txt
python3 -m uvicorn server:app --host 127.0.0.1 --port 9999
```

Optional: point at another transcript:

```bash
DEF_CTERM_PATH=/path/to/other-transcript.txt python3 -m uvicorn server:app --host 127.0.0.1 --port 9999
```

## Try it

```bash
curl -s http://127.0.0.1:9999/__cq/cache/help | jq .
curl -s http://127.0.0.1:9999/__cq/cache/info | jq '.cache-summary.policy-map'
curl -s http://127.0.0.1:9999/health | jq .
```

## Fixtures

Loaded keys come from lines like `url=http://localhost:9999/__cq/cache/<name>` in **`def-cterm.txt`** at the repo root (or `DEF_CTERM_PATH`). Current file includes at least: **`info`**, **`ip-map`**, **`policy-map`**, **`all`**.

## Downstream

Set:

```bash
export DEFENDER_BASE_URL=http://127.0.0.1:9999
```

Then use `retrieval-eval` defender MCP / `mvm_defender_api_runner.py` against this mock.
