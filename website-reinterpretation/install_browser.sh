#!/bin/bash
# Install Playwright and browser binaries

echo "Installing Playwright..."
pip install playwright

echo "Installing browser binaries..."
python3 -m playwright install chromium

echo "Done! Browser support is now available."
