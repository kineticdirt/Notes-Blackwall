#!/usr/bin/env python3
"""
Test sacrificial prompt injection detection and remedy.

Run from project root:
  python test_prompt_injection.py

Or run the module:
  python -m blackwall.prompt_injection.test_detector
"""

import sys
import os

# Ensure blackwall is on path when run from project root
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from blackwall.prompt_injection.test_detector import main

if __name__ == "__main__":
    main()
