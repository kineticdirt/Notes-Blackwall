# Workspace Overseer

Lightweight AI overseer for Cursor workspaces: **small monitoring** and **mild, goal-directed changes**. Not fast or extreme; provides oversight so a larger AI or human can direct the workspace toward a common known goal.

## Intent

- **Monitor**: Lightweight snapshot (file count, recent files, git branch/dirty). No heavy analysis.
- **Mild changes**: Append-only or small scoped edits (e.g. append to `.overseer/overseer.log`, `.overseer/scratchpad.md`). No bulk rewrites. Max N changes per run (default 3).
- **Goal-directed**: One goal per run (env or CLI). Policy decides a small list of actions from observations + goal.

## Directed by a larger AI

- Set **goal** via env `OVERSEE_GOAL` or CLI `--goal "..."`.
- Run one cycle: `python run_overseer.py` or `python -m overseer.cli run`.
- Report (stdout or `--json`) tells the larger AI what was observed and what was applied.
- State in `.overseer/state.json`; log in `.overseer/overseer.log`; scratchpad in `.overseer/scratchpad.md`.

## Usage

```bash
# Default goal from env or built-in
python run_overseer.py

# Custom goal (e.g. set by larger AI)
OVERSEE_GOAL="Keep README and compendium index in sync" python run_overseer.py

# Or
python run_overseer.py --goal "Suggest doc updates only"

# Dry run (no writes)
python run_overseer.py --dry-run

# JSON report
python run_overseer.py --json
```

## Env

| Env | Meaning |
|-----|--------|
| `OVERSEE_GOAL` | Known goal for this run. |
| `OVERSEE_WORKSPACE` | Workspace root (default `.`). |
| `OVERSEE_DRY_RUN` | 1/true/yes = no writes. |
| `OVERSEE_MAX_CHANGES` | Max mild changes per run (default 3). |

## Files

- `.overseer/state.json` — Last run, observations summary, applied changes.
- `.overseer/overseer.log` — Append-only run log.
- `.overseer/scratchpad.md` — Append-only notes (e.g. suggestions for docs/README).
