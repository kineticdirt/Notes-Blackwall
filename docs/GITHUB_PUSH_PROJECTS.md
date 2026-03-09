# Pushing Projects to Separate GitHub Repos

This guide gets each project folder into its **own GitHub repo**. You must log in to GitHub once; the script handles the rest.

## One-time: Log in to GitHub

**Option A – GitHub CLI (recommended, script can create repos for you)**

1. Install: `brew install gh`
2. Log in: `gh auth login`
   - Choose GitHub.com, HTTPS or SSH, and complete the browser/auth flow.

**Option B – No CLI**

- Create repos manually at https://github.com/new when the script asks.
- Git push will use your existing SSH keys or credential helper.

## Run the script

From the workspace root (e.g. `"Notes - Blackwall"`):

```bash
export GITHUB_USER=yourusername
```

**If you use GitHub CLI (repos created and pushed automatically):**

```bash
USE_GH=1 ./scripts/push-projects-to-github.sh
```

**If you don’t use `gh` (repos created by you):**

```bash
./scripts/push-projects-to-github.sh
```

Then for each project the script will print:

1. Link to create the repo: `https://github.com/new?name=<repo_name>`
2. The exact `git remote add` and `git push` commands.

Create each repo (private or public), then run the printed push commands. Repos are prepared under a temp dir; the script prints its path and a `rm -rf` command to clean up after you’re done.

## Projects pushed

The script pushes **all local content** as many small repos:

- **Root:** `notes-blackwall-root` (all root-level .md, run_*.py, test_*.py, docker-compose, worktree_manager, worktree-spec.json)
- **Folders:** agent-system, assistant, blackwall, cloud_agents_notifications, compendium, docs, grainrad-poc, hooks, library, ledger, nightshade-tracker, orchestrator-node, overseer, scripts, toolbox_test, website-reinterpretation, workflow-canvas, worktree-orchestration, worktree-orchestration-v2, worktrees

Edit `PROJECTS` in `scripts/push-projects-to-github.sh` to add or remove folders.

## Safety

- The script reuses the workspace root `.gitignore`, so `.env`, `secrets.env`, and other ignored paths are not pushed.
- Do not add API keys or secrets to the repo; use env vars or a secrets store.
