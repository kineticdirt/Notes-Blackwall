# Blackwall Autonomous System - Quick Start

## What is Autonomous?

Blackwall agents **operate independently** - you set goals, they achieve them autonomously.

## 5-Minute Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Your First Autonomous Goal

```bash
python autonomous_cli.py achieve "Protect all content in this directory"
```

The system will:
- Analyze the goal
- Decide which agents are needed
- Coordinate agents automatically
- Complete the goal
- Report results

### 3. Check Status

```bash
python autonomous_cli.py status
```

## Common Autonomous Tasks

### Protect Content Autonomously

```bash
# Single file
python autonomous_cli.py protect document.txt

# Entire directory
python autonomous_cli.py batch-protect ./content/
```

### Complex Autonomous Workflows

```bash
# Coordinate multiple agents
python autonomous_cli.py coordinate "Protect content, generate tests, and create documentation"
```

## How Autonomous Agents Work

1. **You set a goal** → `achieve "protect all images"`
2. **Orchestrator analyzes** → Decides which agents needed
3. **Agents coordinate** → Discover each other, form teams
4. **Agents work autonomously** → Make decisions, adapt strategies
5. **Goal completed** → Results reported automatically

## Key Concepts

- **Autonomous**: Agents work without constant supervision
- **Self-Coordinating**: Agents discover and work together
- **Goal-Oriented**: You set goals, agents achieve them
- **Adaptive**: Agents learn and adapt strategies

## Next Steps

- Read [README_AUTONOMOUS.md](README_AUTONOMOUS.md) for full documentation
- See [AUTONOMOUS_DESIGN.md](AUTONOMOUS_DESIGN.md) for architecture details
