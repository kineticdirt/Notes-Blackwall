# DaDumpMan

Reference dump: DevOps, ops, AWS, orchestration, and load-balancing notes.

## Contents

- **[docs/DevOps-Ops-Reference.md](docs/DevOps-Ops-Reference.md)** — DevOps flow, scripting terms, distributed-systems testing, mock/dev envs, AWS services, orchestrators, load balancers.
- **[docs/GITHUB-CONNECT.md](docs/GITHUB-CONNECT.md)** — How to connect this repo to GitHub (CLI vs PAT).
- **[scripts/setup-github-pat.sh](scripts/setup-github-pat.sh)** — One-time “paste your PAT” script; then `git push` works.

## Use this folder as the repo

From this directory:

```bash
git init
git add .
git commit -m "Add DevOps & Ops reference; GitHub connect guide"
git branch -M main
git remote add origin git@github.com:kineticdirt/DaDumpMan.git
git push -u origin main
```

Set up auth first: run `./scripts/setup-github-pat.sh` and paste your PAT when prompted, or see [docs/GITHUB-CONNECT.md](docs/GITHUB-CONNECT.md).
