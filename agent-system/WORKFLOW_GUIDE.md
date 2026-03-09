# Workflow Guide: Cleanup -> Test -> Documentation

## Overview

This workflow uses three specialized agents that work together through a shared scratchpad:

1. **Cleanup Agent** - Cleans up and refactors code
2. **Test Agent** - Writes test cases (uses cleanup notes)
3. **Documentation Agent** - Writes documentation (uses all notes)

## How It Works

### The Scratchpad System

All agents append to a shared scratchpad (`ledger/scratchpad.json`) with sections:
- **overview**: Project overview and workflow status
- **code_notes**: Cleanup agent findings and summaries
- **test_notes**: Test agent analysis and test summaries
- **doc_notes**: Documentation agent notes and summaries
- **issues**: Issues found by any agent
- **todo**: TODO items

### Workflow Phases

#### Phase 1: Cleanup
1. Cleanup agent analyzes codebase
2. Identifies cleanup opportunities
3. Performs cleanup operations
4. **Appends findings to scratchpad** (code_notes section)

#### Phase 2: Testing
1. Test agent reads cleanup notes from scratchpad
2. Analyzes what needs testing
3. Writes test cases
4. **Appends test notes to scratchpad** (test_notes section)

#### Phase 3: Documentation
1. Documentation agent reads ALL notes (cleanup + test)
2. Understands the full context
3. Writes comprehensive documentation
4. **Appends doc notes to scratchpad** (doc_notes section)

## Usage

### Basic Workflow

```python
from workflow_coordinator import WorkflowCoordinator

# Initialize
workflow = WorkflowCoordinator()

# Run full workflow
workflow.run_full_workflow(
    target_path="nightshade-tracker",
    files=["core/watermarking.py", "core/poisoning.py"]
)

# Check status
status = workflow.get_workflow_status()
print(status)

# View scratchpad
scratchpad = workflow.view_scratchpad()
print(scratchpad)
```

### Step-by-Step Workflow

```python
from workflow_coordinator import WorkflowCoordinator

workflow = WorkflowCoordinator()

# Step 1: Cleanup
workflow._run_cleanup_phase("nightshade-tracker", ["core/watermarking.py"])

# View cleanup notes
code_notes = workflow.view_scratchpad("code_notes")

# Step 2: Tests (uses cleanup notes)
workflow._run_test_phase("nightshade-tracker", ["core/watermarking.py"])

# Step 3: Documentation (uses all notes)
workflow._run_doc_phase("nightshade-tracker", ["core/watermarking.py"])
```

### Individual Agent Usage

```python
from agents.cleanup_agent import CleanupAgent
from agents.test_agent import TestAgent
from agents.doc_agent import DocAgent

# Cleanup Agent
cleanup = CleanupAgent()
cleanup.analyze_codebase("nightshade-tracker")
cleanup.cleanup_code(["core/watermarking.py"], "general")
cleanup.report_cleanup_summary("Cleaned up 5 files, removed unused imports")

# Test Agent (reads cleanup notes)
test = TestAgent()
test.analyze_for_tests("nightshade-tracker")
test.write_tests(["core/watermarking.py"], "unit")
test.report_test_summary("Wrote 15 test cases", coverage=87.5)

# Doc Agent (reads all notes)
doc = DocAgent()
doc.analyze_for_docs("nightshade-tracker")
doc.write_documentation(["core/watermarking.py"], "api")
doc.report_doc_summary("Created API docs", ["docs/watermarking_api.md"])
```

## Scratchpad Structure

The scratchpad (`ledger/scratchpad.json`) contains:

```json
{
  "sections": {
    "overview": [
      {
        "content": "Starting workflow...",
        "agent_id": "workflow_coordinator",
        "timestamp": "2025-01-07T...",
        "metadata": {}
      }
    ],
    "code_notes": [
      {
        "content": "Cleanup Agent: Analyzing...",
        "agent_id": "cleanup-001",
        "timestamp": "...",
        "metadata": {"intent_id": "...", "target": "..."}
      }
    ],
    "test_notes": [...],
    "doc_notes": [...],
    "issues": [...],
    "todo": []
  },
  "metadata": {
    "workflow_status": "completed"
  }
}
```

## How Agents Use the Scratchpad

### Cleanup Agent
- **Writes to**: `code_notes`, `issues`
- **Reads from**: Nothing (first in pipeline)
- **Purpose**: Document what was cleaned up

### Test Agent
- **Writes to**: `test_notes`, `issues`
- **Reads from**: `code_notes` (to understand what was cleaned)
- **Purpose**: Document test coverage and test cases

### Documentation Agent
- **Writes to**: `doc_notes`, `overview`
- **Reads from**: `code_notes`, `test_notes`, `issues` (all context)
- **Purpose**: Create comprehensive documentation

## Benefits

1. **Context Preservation**: Each agent builds on previous work
2. **No Race Conditions**: Agents declare intents before acting
3. **Full Visibility**: All notes in one place (scratchpad)
4. **Coordination**: Agents can see what others are doing
5. **Traceability**: Complete audit trail of workflow

## Example Output

After running workflow:

```
=== Workflow Status ===
Status: completed

Scratchpad Entries:
  overview: 3 entries
  code_notes: 5 entries
  test_notes: 4 entries
  doc_notes: 3 entries
  issues: 0 entries

=== Scratchpad Overview ===
[workflow_coordinator] Starting full workflow for: nightshade-tracker
[workflow_coordinator] Workflow completed successfully!

=== Code Notes ===
[cleanup-001] Cleanup Agent: Analyzing nightshade-tracker...
[cleanup-001] CLEANUP SUMMARY: Cleaned 3 files, removed unused imports

=== Test Notes ===
[test-001] Test Agent: Analyzing nightshade-tracker...
[test-001] TEST SUMMARY: Wrote 15 test cases, Coverage: 85.0%

=== Documentation Notes ===
[doc-001] Doc Agent: Analyzing nightshade-tracker...
[doc-001] DOCUMENTATION SUMMARY: Created API docs
```

## Running the Example

```bash
cd agent-system
python workflow_example.py
```

This will demonstrate the full workflow and show how agents coordinate through the scratchpad.
