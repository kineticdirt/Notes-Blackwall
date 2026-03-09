# Worktree Orchestration System

Minimal working scaffold for evaluating multiple solutions using worktree directories.

## Quick Start

```bash
# Make scripts executable
chmod +x test_harness/run_tests.sh
chmod +x worktree_manager.py run_orchestration.py

# Run full orchestration
python3 run_orchestration.py
```

## File Layout

```
.
├── worktree-spec.json          # Configuration spec
├── worktree_manager.py          # Creates/manages worktree directories
├── run_orchestration.py         # Main orchestration script
├── test_harness/
│   └── run_tests.sh            # Shared test harness
├── worktrees/                  # Created worktree directories
│   ├── solution-1/
│   │   ├── solution/          # Place solution files here
│   │   └── critique/          # Place critique files here
│   ├── solution-2/
│   └── solution-3/
├── solutions/                  # Centralized solution storage
├── critiques/                  # Centralized critique storage
├── results/                    # Test results
└── report.html                 # Generated report
```

## Usage

### 1. Setup Worktrees
```bash
python3 worktree_manager.py
```

### 2. Add Solutions
Place your solution files in each worktree's `solution/` directory:
```bash
cp my_solution.py worktrees/solution-1/solution/
echo "# My Solution" > worktrees/solution-1/solution/README.md
```

### 3. Run Tests
```bash
# Test individual worktree
./test_harness/run_tests.sh worktrees/solution-1

# Or run full orchestration
python3 run_orchestration.py
```

### 4. View Report
Open `report.html` in a browser.

## Configuration

Edit `worktree-spec.json` to:
- Add/remove worktrees
- Adjust scoring weights
- Change test harness settings
- Configure report output

## What's Implemented Now

✅ **Core Structure**
- Worktree creation and management
- Test harness runner
- Basic scoring (file count, Python files, README, syntax)
- HTML report generation

✅ **Test Harness Checks**
- Solution file existence
- Python file detection
- README presence
- Syntax validation

## What to Implement Later

🔲 **Enhanced Scoring**
- Performance benchmarks
- Code quality metrics (complexity, style)
- Test coverage analysis
- Custom scoring plugins

🔲 **Advanced Features**
- Git integration (if repo becomes git)
- Parallel test execution
- Caching of test results
- Comparison diffing between solutions
- Critique generation automation

🔲 **Report Enhancements**
- Export to JSON/CSV
- Historical tracking
- Charts and visualizations
- Detailed code analysis

## Example Workflow

```bash
# 1. Create worktrees
python3 worktree_manager.py

# 2. Add solution to worktree-1
cat > worktrees/solution-1/solution/main.py <<EOF
def solve():
    return "solution"
EOF

# 3. Run orchestration
python3 run_orchestration.py

# 4. View results
open report.html
```

## Notes

- This is a **minimal scaffold** - extend as needed
- Test harness is bash-based for simplicity
- Scoring is simplified - customize `compute_scores()` for real metrics
- No git required - uses plain directories
- Results stored as JSON for easy parsing
