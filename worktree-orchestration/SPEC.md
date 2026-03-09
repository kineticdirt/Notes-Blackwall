# Worktree Orchestration v2.0.0 Specification

## Version
**2.0.0**

## Purpose
A directory-based multi-agent competition system that enables agents to compete in isolated workspaces without requiring git worktrees or git configuration changes.

## Core Concepts

### Worktree
A directory-based isolated workspace for a competitor in a specific round. Each worktree is a separate directory that contains:
- Competitor's solution files
- Test execution environment
- Isolated from other competitors' worktrees

### Competitor
An agent participating in the competition. Each competitor:
- Has a unique identifier
- Has an associated script/executable
- Can submit solutions and critiques
- Operates in isolated worktrees per round

### Round
A single competition iteration where:
- All competitors receive the same challenge/problem
- Competitors submit solutions
- Competitors can critique other solutions
- Solutions are tested and scored
- Results are collected and stored

### Arena
The orchestration system that:
- Manages rounds
- Coordinates competitor submissions
- Executes tests
- Collects results
- Stores artifacts

## Configuration Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "version": "2.0.0",
  "type": "object",
  "required": ["version", "competition", "worktree", "arena"],
  "properties": {
    "version": {
      "type": "string",
      "pattern": "^2\\.0\\.0$",
      "description": "Must be exactly '2.0.0'"
    },
    "competition": {
      "type": "object",
      "required": ["name", "rounds", "max_competitors"],
      "properties": {
        "name": {
          "type": "string",
          "minLength": 1,
          "maxLength": 100,
          "description": "Competition name"
        },
        "rounds": {
          "type": "integer",
          "minimum": 1,
          "maximum": 100,
          "description": "Number of competition rounds"
        },
        "max_competitors": {
          "type": "integer",
          "minimum": 1,
          "maximum": 50,
          "description": "Maximum number of competitors"
        }
      }
    },
    "worktree": {
      "type": "object",
      "required": ["base_path"],
      "properties": {
        "base_path": {
          "type": "string",
          "pattern": "^[^/].*",
          "description": "Relative path for worktree base (no leading slash)"
        },
        "template_path": {
          "type": "string",
          "pattern": "^[^/].*",
          "description": "Optional template directory to copy into worktrees"
        },
        "cleanup_after_round": {
          "type": "boolean",
          "default": false,
          "description": "Automatically cleanup worktrees after round ends"
        }
      }
    },
    "arena": {
      "type": "object",
      "required": ["test_command", "timeout_seconds"],
      "properties": {
        "test_command": {
          "type": "string",
          "minLength": 1,
          "description": "Command to execute tests (relative to worktree)"
        },
        "timeout_seconds": {
          "type": "integer",
          "minimum": 1,
          "maximum": 3600,
          "description": "Maximum test execution time in seconds"
        },
        "parallel_tests": {
          "type": "boolean",
          "default": false,
          "description": "Run tests in parallel across competitors"
        }
      }
    }
  }
}
```

## Worktree Structure

### Directory Layout
```
{worktree.base_path}/
  ├── wt_{competitor_id}_r{round_num}/
  │   ├── solution/          # Competitor's solution files
  │   ├── tests/             # Test files (copied from template if provided)
  │   └── .metadata.json     # Worktree metadata
```

### Naming Convention
- Worktree directories: `wt_{competitor_id}_r{round_num}`
- Competitor IDs: Alphanumeric + underscores, max 50 chars
- Round numbers: Zero-padded, e.g., `001`, `002`

## Artifact Storage

### Directory Structure
```
.shared-cache/
  ├── rounds/
  │   └── round_{round_num}/
  │       ├── solutions/
  │       │   └── {competitor_id}_{timestamp}.json
  │       ├── critiques/
  │       │   └── {competitor_id}_{target_id}_{timestamp}.json
  │       └── results.json
  └── competitors/
      └── {competitor_id}.json
```

### Solution Artifact Format
```json
{
  "competitor_id": "string",
  "round_num": "integer",
  "timestamp": "ISO8601 datetime",
  "worktree_path": "relative path",
  "files": [
    {
      "path": "relative path in worktree",
      "size": "integer bytes",
      "hash": "sha256 hex string"
    }
  ],
  "metadata": {
    "submission_time": "ISO8601 datetime",
    "test_results": "object (after testing)"
  }
}
```

### Critique Artifact Format
```json
{
  "competitor_id": "string",
  "round_num": "integer",
  "target_solution_id": "string",
  "timestamp": "ISO8601 datetime",
  "critique_text": "string",
  "scores": {
    "clarity": "integer 1-10",
    "correctness": "integer 1-10",
    "efficiency": "integer 1-10"
  }
}
```

### Results Format
```json
{
  "round_num": "integer",
  "start_time": "ISO8601 datetime",
  "end_time": "ISO8601 datetime",
  "solutions": [
    {
      "competitor_id": "string",
      "test_passed": "boolean",
      "test_output": "string",
      "test_duration_ms": "integer",
      "score": "float"
    }
  ],
  "critiques": [
    {
      "critique_id": "string",
      "competitor_id": "string",
      "target_solution_id": "string"
    }
  ]
}
```

## API/CLI Commands

### Initialization
```bash
init <config.json>
```
- Validates configuration
- Creates `.shared-cache/` directory structure
- Initializes competition state

### Competitor Management
```bash
competitor register <name> <script_path>
```
- Registers a new competitor
- Validates script exists and is executable
- Stores competitor metadata

```bash
competitor list
```
- Lists all registered competitors

```bash
competitor show <competitor_id>
```
- Shows competitor details

### Worktree Management
```bash
worktree create <competitor_id> <round_num>
```
- Creates isolated worktree directory
- Copies template if configured
- Returns worktree path

```bash
worktree list [round_num]
```
- Lists all worktrees (optionally filtered by round)

```bash
worktree show <competitor_id> <round_num>
```
- Shows worktree details and contents

### Arena Operations
```bash
arena start-round <round_num>
```
- Initializes round
- Creates worktrees for all competitors
- Sets round state to "active"

```bash
arena submit-solution <competitor_id> <round_num> <solution_path>
```
- Copies solution files to competitor's worktree
- Validates solution structure
- Creates solution artifact

```bash
arena submit-critique <competitor_id> <round_num> <target_solution_id> <critique_path>
```
- Stores critique referencing target solution
- Creates critique artifact
- Validates target solution exists

```bash
arena test <round_num>
```
- Executes test command in each competitor's worktree
- Collects test results
- Updates solution artifacts with test results

```bash
arena end-round <round_num>
```
- Finalizes round
- Collects all results
- Generates results.json
- Optionally cleans up worktrees

### Artifact Management
```bash
artifacts list <round_num>
```
- Lists all artifacts for a round

```bash
artifacts show <artifact_id>
```
- Shows artifact contents

```bash
artifacts export <round_num> <output_path>
```
- Exports all round artifacts to output path

### Cleanup
```bash
cleanup [--force] [--round <round_num>]
```
- Removes worktrees
- With confirmation unless --force
- Optionally filter by round

## Error Handling

### Validation Errors
- Config validation failures: Clear error messages with schema violations
- Path validation failures: Reject absolute paths, invalid characters
- Competitor validation: Script must exist and be executable

### Runtime Errors
- Worktree creation failures: Rollback, clear error message
- Test execution failures: Capture stderr, timeout handling
- Artifact storage failures: Atomic writes, corruption detection

### Error Codes
- `CONFIG_INVALID`: Configuration validation failed
- `COMPETITOR_NOT_FOUND`: Competitor ID doesn't exist
- `ROUND_NOT_ACTIVE`: Round not in active state
- `WORKTREE_EXISTS`: Worktree already exists
- `TEST_TIMEOUT`: Test execution exceeded timeout
- `TEST_FAILED`: Test execution returned non-zero exit code

## Security Requirements

1. **Path Safety**: All paths validated, no absolute paths, no traversal
2. **Command Safety**: Test commands executed with explicit args, no shell injection
3. **Isolation**: Worktrees isolated, no cross-contamination
4. **Resource Limits**: Timeouts enforced, disk space checks
5. **Input Validation**: All inputs validated before processing

## Performance Considerations

1. **Worktree Creation**: Template copying can be slow for large templates
2. **Test Execution**: Sequential by default, parallel option available
3. **Artifact Storage**: JSON files, suitable for small-medium datasets
4. **Cleanup**: Can be slow for many worktrees, consider async cleanup

## Limitations

1. **No Git Integration**: Cannot leverage git features (branches, history, etc.)
2. **Disk Usage**: Full directory copies, no deduplication
3. **Concurrency**: Limited concurrent round support (lock-based)
4. **Scalability**: Designed for < 50 competitors, < 100 rounds
5. **Platform**: Unix-like systems (Linux, macOS), Windows support limited

## Future Enhancements

1. Hardlink support for template copying (reduced disk usage)
2. Parallel test execution with resource monitoring
3. Database backend for artifact storage (optional)
4. Web UI for competition monitoring
5. Git integration (optional, opt-in)
