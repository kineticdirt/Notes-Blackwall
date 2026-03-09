"""
Sample test file that will be copied into worktrees.
"""
import pytest
from pathlib import Path


def test_solution_exists():
    """Test that solution directory exists."""
    solution_dir = Path("solution")
    assert solution_dir.exists(), "Solution directory should exist"


def test_solution_file():
    """Test that solution file exists."""
    solution_file = Path("solution") / "my_solution.py"
    if solution_file.exists():
        # If solution exists, verify it's valid Python
        code = solution_file.read_text()
        compile(code, solution_file, 'exec')
    else:
        pytest.skip("Solution file not found")
