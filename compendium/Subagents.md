# Subagents — Claude Sub-Agent System

Expanded documentation for the **Claude subagents**: specialized agents invoked by Claude Code for cleanup, testing, documentation, code, research, and review. See also [[Agent-System]] (coordinator, ledger) and [[Agent-System#Claude integration]].

---

## Overview

- **Location**: `agent-system/` (Python) and `agent-system/.claude/agents/` (Claude configs).
- **Role**: Claude Code automatically invokes subagents based on task; each has specific tools and a defined workflow.
- **Coordination**: Subagents use [[Agent-System#Ledger]] (AI_GROUPCHAT) and [[Agent-System#Scratchpad]] for communication and conflict avoidance.

---

## Configured Subagents (`.claude/agents/`)

Three subagents are defined as markdown files with YAML frontmatter. Claude Code discovers them and invokes by task.

### 1. Cleanup Agent (`cleanup-agent.md`)

| Field | Value |
|-------|--------|
| **Name** | cleanup-agent |
| **Description** | Code cleanup, refactoring, optimization; invoked when cleanup is needed. |
| **Tools** | read_file, write_file, search_replace, grep, codebase_search, read_lints |
| **Model** | sonnet |

**Responsibilities**:
- Code analysis: unused imports, duplication, dead code, formatting, performance.
- Refactoring: extract patterns, simplify logic, naming, organization.
- Quality: fix linting, type hints, documentation, imports.

**Workflow**: Analyze → Plan (scratchpad) → Refactor → Verify (lints, tests) → Document in scratchpad.

**Communication**: Log to scratchpad, report issues, coordinate with test and doc agents; use ledger to declare intent and avoid conflicts.

---

### 2. Test Agent (`test-agent.md`)

| Field | Value |
|-------|--------|
| **Name** | test-agent |
| **Description** | Comprehensive test cases; invoked when test coverage or new tests are needed. |
| **Tools** | read_file, write_file, codebase_search, grep, read_lints |
| **Model** | sonnet |

**Responsibilities**:
- Test analysis: coverage gaps, edge cases, error paths.
- Test writing: unit, integration, edge/error, performance when needed.
- Quality: clear names, setup/teardown, isolation, assertions.

**Workflow**: Analyze (code + cleanup notes) → Plan → Write tests → Verify → Document coverage in scratchpad.

**Frameworks**: Python (pytest, unittest), JS/TS (Jest, Mocha), others as appropriate.

---

### 3. Doc Agent (`doc-agent.md`)

| Field | Value |
|-------|--------|
| **Name** | doc-agent |
| **Description** | Documentation; invoked when docs are needed or code changes require doc updates. |
| **Tools** | read_file, write_file, codebase_search, grep |
| **Model** | sonnet |

**Responsibilities**:
- Doc analysis: missing/outdated docs, types needed.
- Writing: API docs, user guides, comments, READMEs.
- Quality: clear structure, examples, up-to-date.

**Workflow**: Analyze (code, cleanup, test notes) → Plan → Write → Review → Report summary in scratchpad.

---

## Python Implementations (`agent-system/agents/`)

Each subagent has a Python class extending `BaseAgent` (see [[Agent-System#Base Agent]]) and using the [[Agent-System#Scratchpad]].

| Agent | Class | File | Specialization |
|-------|--------|------|----------------|
| Cleanup | `CleanupAgent` | cleanup_agent.py | cleanup, refactor, optimize |
| Test | `TestAgent` | test_agent.py | unit/integration tests, coverage |
| Doc | `DocAgent` | doc_agent.py | API, README, guides, comments |
| Code | `CodeAgent` | code_agent.py | implementation |
| Research | `ResearchAgent` | research_agent.py | research, analysis |
| Review | `ReviewAgent` | review_agent.py | code review |

**DocAgent** (example):
- `analyze_for_docs(target_path)` — declare intent, read code/test notes, append to `doc_notes`.
- `write_documentation(files, doc_type)` — declare intent, gather scratchpad context, append doc_notes.
- `report_doc_summary(summary, files_created)` — write summary to scratchpad.

**TestAgent** (example):
- `analyze_for_tests(target_path)` — declare intent, read code_notes, append test_notes.
- `write_tests(files, test_type)` — declare intent, use code_notes, append test_notes.
- `report_test_summary(summary, coverage)`, `report_test_issues(issues)`.

**CleanupAgent**: Uses scratchpad for findings and coordination with test/doc agents; declares intent before modifying files.

---

## Expanding Subagents

1. **Add a new Claude config**: Create `agent-system/.claude/agents/<name>-agent.md` with YAML frontmatter (`name`, `description`, `tools`, `model`) and body (responsibilities, workflow, communication).
2. **Add a new Python agent**: In `agent-system/agents/` add `<name>_agent.py` with a class extending `BaseAgent`, then register in `agents/__init__.py`.
3. **Verify**: Run `agent-system/setup_claude_integration.py` to check subagent configuration.

---

## Related

- [[Agent-System]] — Coordinator, ledger, task queue, base agent, scratchpad.
- [[Architecture-Overview]] — Where subagents sit in the stack.
- [[Blackwall-Agents]] — Blackwall-side agents (detection, protection) that differ from Claude subagents.
