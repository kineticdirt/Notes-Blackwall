#!/usr/bin/env python3
"""
Run the workspace overseer (one cycle). For Cursor or a larger AI to invoke.

Goal from env OVERSEE_GOAL or pass --goal "..." for mild, goal-directed oversight.
"""

import sys
import os
from pathlib import Path

# Project root
ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from overseer.cli import main

if __name__ == "__main__":
    os.chdir(ROOT)
    main()
