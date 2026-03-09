# CLI Hub

Unified command-line interface for all Cequence BlackWall tools.

## Why

Instead of remembering which directory to `cd` into and which CLI to run:

```bash
# Before: scattered CLIs
cd blackwall && python -m blackwall.cli protect ...
cd nightshade-tracker && python -m nightshade ...
cd security-toolkit && python -m src scan ...
cd data-pipeline && python -m src.pipeline ...
```

One entry point:

```bash
# After: unified CLI
cq blackwall protect --text "hello"
cq nightshade process --input image.png
cq security scan --secrets
cq pipeline run --mode batch
cq overseer status
cq gateway health
```

## Install

```bash
pip install -e .
```

This installs `cq` as a global command.

## Commands

| Command | Dispatches To | Description |
|---------|---------------|-------------|
| `cq blackwall` | `blackwall/` | AI text/image protection |
| `cq nightshade` | `nightshade-tracker/` | Image/text poisoning CLI |
| `cq security` | `security-toolkit/` | Security scanning |
| `cq pipeline` | `data-pipeline/` | Data pipeline ops |
| `cq overseer` | `overseer/` | Overseer status and control |
| `cq gateway` | `api-gateway/` | Gateway health and config |
| `cq workflow` | `workflow-canvas/` | Workflow management |
| `cq infra` | `infrastructure-blueprints/` | Deploy helpers |

## Adding a New Command

1. Create `src/commands/your_tool.py`
2. Define a Click group or command
3. Register it in `src/main.py`
