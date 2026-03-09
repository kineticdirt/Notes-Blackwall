#!/usr/bin/env python3
"""
Sample competitor script.
This is a template that competitors can use as a starting point.
"""
import sys
from pathlib import Path


def main():
    """Main competitor entry point."""
    if len(sys.argv) < 2:
        print("Usage: sample_competitor.py <worktree_path>")
        sys.exit(1)
    
    worktree_path = Path(sys.argv[1])
    
    # Competitor logic here
    print(f"Competitor working in: {worktree_path}")
    
    # Example: Create a solution file
    solution_file = worktree_path / "solution" / "my_solution.py"
    solution_file.write_text("""
# My solution
def solve():
    return "Hello, World!"
""")
    
    print("Solution created!")


if __name__ == "__main__":
    main()
