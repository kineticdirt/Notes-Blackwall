# Worktree System Quick Start

Quick guide to get started with worktrees, skills, and subagents.

## Installation

The worktree system requires:
- Python 3.8+
- PyYAML (for skill loading)

Install dependencies:
```bash
pip install pyyaml
```

## Quick Start

### 1. Create Your First Worktree

```python
from blackwall.worktrees import UnifiedWorktreeManager

manager = UnifiedWorktreeManager()

# Create a worktree with agents and skills
worktree = manager.create_worktree(
    name="My Team",
    description="Development team",
    agent_types=["code", "test", "doc"],
    skills=["code-analysis", "documentation"]
)
```

### 2. Assign Tasks

```python
# Assign a task to the worktree
task_id = manager.assign_task_to_worktree(
    worktree_id=worktree.worktree_id,
    task_description="Implement new feature",
    agent_type="code",
    priority=8
)
```

### 3. Create Custom Skills

Create a skill file in `.skills/my-skill.md`:

```markdown
---
name: my-skill
description: My custom skill
version: 1.0.0
tools: [read_file, write_file]
---

# My Skill

## Workflow
1. Do this
2. Then that

## Examples
- Example usage
```

Then reload:
```bash
python -m blackwall.worktrees.cli reload-skills
```

### 4. Use CLI

```bash
# Create worktree
python -m blackwall.worktrees.cli create "My Team" \
  --agent-types "code,test" \
  --skills "code-analysis"

# List worktrees
python -m blackwall.worktrees.cli list

# Assign task
python -m blackwall.worktrees.cli task <worktree-id> "Do something"
```

## Example Workflow

```python
from blackwall.worktrees import UnifiedWorktreeManager

# Initialize
manager = UnifiedWorktreeManager()

# Create worktree for code analysis
worktree = manager.create_worktree(
    name="Code Analysis Team",
    agent_types=["code", "cleanup"],
    skills=["code-analysis"]
)

# Assign analysis task
task_id = manager.assign_task_to_worktree(
    worktree_id=worktree.worktree_id,
    task_description="Analyze codebase for quality issues",
    agent_type="code"
)

# Check status
status = manager.get_worktree_status(worktree.worktree_id)
print(f"Agents: {status['agent_count']}")
print(f"Skills: {status['skills']}")
```

## File Structure

After running, you'll have:

```
.worktrees/              # Worktree data
├── wt-<id>/           # Individual worktree
│   ├── config.json
│   └── ledger/
└── worktree.db        # SQLite database

.skills/                # Skills (nested markdown)
├── code-analysis.md
├── protection.md
└── documentation.md
```

## Next Steps

- Read [README.md](README.md) for full documentation
- Create custom skills for your use cases
- Integrate with your agent workflows
- Use the database API for UI state management
