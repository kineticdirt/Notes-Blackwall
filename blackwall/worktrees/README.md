# Worktree System

Worktree system for organizing multiple agents, skills, and tasks. Based on the whiteboard design: "Worktrees for organizing multiple agents".

## Overview

The worktree system provides:

- **Worktrees**: Logical grouping of agents for organized multi-agent coordination
- **Skills**: Nested markdown files defining agent capabilities
- **Subagents**: Integration with specialized agents (code, cleanup, test, doc, research, review)
- **Database**: SQLite database for UI state and task completion tracking

## Architecture

```
worktrees/
├── worktree.py          # Worktree and WorktreeManager classes
├── worktree_db.py       # Database layer for UI and task tracking
├── worktree_manager.py  # Unified manager integrating all components
├── cli.py               # Command-line interface
└── skills/
    ├── skill.py         # Skill data class
    └── skill_loader.py  # Load skills from nested markdown files
```

## Concepts

### Worktrees

A worktree is a logical grouping of agents that work together. Each worktree has:
- Its own coordinator and ledger
- Isolated agent communication
- Assigned skills
- Task queue

### Skills

Skills are defined in nested markdown files (`.skills/*.md`) with YAML frontmatter:

```markdown
---
name: skill-name
description: Skill description
version: 1.0.0
tools: [tool1, tool2]
resources: [resource1]
---

# Skill Name

## Workflow
1. Step one
2. Step two

## Examples
- Example 1
- Example 2
```

### Subagents

Subagents are specialized agents that can be assigned to worktrees:
- `code`: Code generation and modification
- `cleanup`: Code cleanup and refactoring
- `test`: Test writing
- `doc`: Documentation generation
- `research`: Research and analysis
- `review`: Code review

## Usage

### CLI

```bash
# Create a worktree
python -m blackwall.worktrees.cli create "My Worktree" \
  --agent-types "code,cleanup,test" \
  --skills "code-analysis,documentation"

# List worktrees
python -m blackwall.worktrees.cli list

# Show worktree details
python -m blackwall.worktrees.cli show <worktree-id>

# Assign a task
python -m blackwall.worktrees.cli task <worktree-id> "Analyze codebase"

# List skills
python -m blackwall.worktrees.cli skills

# Reload skills
python -m blackwall.worktrees.cli reload-skills
```

### Python API

```python
from blackwall.worktrees import UnifiedWorktreeManager

# Initialize manager
manager = UnifiedWorktreeManager()

# Create worktree
worktree = manager.create_worktree(
    name="Development Team",
    description="Team for development tasks",
    agent_types=["code", "test", "doc"],
    skills=["code-analysis", "documentation"]
)

# Assign task
task_id = manager.assign_task_to_worktree(
    worktree_id=worktree.worktree_id,
    task_description="Implement new feature",
    agent_type="code",
    priority=8
)

# Get status
status = manager.get_worktree_status(worktree.worktree_id)
print(status)
```

## Database Schema

The database tracks:
- **worktrees**: Worktree configurations
- **tasks**: Task assignments and status
- **task_completions**: Completed task records
- **ui_state**: UI state for worktrees
- **skills_registry**: Registered skills

## Skills Directory

Skills are stored in `.skills/` directory. Example skills:
- `code-analysis.md`: Code quality analysis
- `protection.md`: Content protection
- `documentation.md`: Documentation generation

## Integration with Agent System

The worktree system integrates with:
- `agent-system/`: Base agent classes and coordinator
- `blackwall/agents/`: Blackwall-specific agents
- MCP tools: Available tools are listed in skills

## File Structure

```
.worktrees/              # Worktree data
├── wt-<id>/            # Individual worktree
│   ├── config.json     # Worktree config
│   └── ledger/         # Agent ledger
│       └── AI_GROUPCHAT.json
└── worktree.db         # SQLite database

.skills/                 # Skills directory
├── code-analysis.md
├── protection.md
└── documentation.md
```

## Next Steps

- [ ] Add Airflow integration for workflow orchestration
- [ ] Create MCP UI using nested markdown files
- [ ] Add worktree visualization
- [ ] Implement skill dependencies
- [ ] Add worktree templates
