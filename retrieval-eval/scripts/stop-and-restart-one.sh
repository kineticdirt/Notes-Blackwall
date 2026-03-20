#!/usr/bin/env bash
# Stop ALL run_sequential.py and caffeinate wrappers, then start exactly ONE with nohup + caffeinate.
# Run from: retrieval-eval/ (or project root)
set -e
cd "$(dirname "$0")/.."
RESULTS="results"
LOG="$RESULTS/run.log"

echo "Stopping any existing run_sequential.py and caffeinate (this run)..."
pkill -f "run_sequential.py --dataset default" || true
pkill -f "caffeinate -i python3 run_sequential.py" || true
sleep 2
if pgrep -f "run_sequential.py" >/dev/null; then
  echo "WARNING: Some run_sequential.py still running. Kill manually: pgrep -af run_sequential"
  exit 1
fi

echo "Starting single background run (resume will skip completed runs)..."
mkdir -p "$RESULTS"
# PYTHONUNBUFFERED=1 so run.log gets lines in real time (no TTY under nohup)
nohup env PYTHONUNBUFFERED=1 caffeinate -i python3 run_sequential.py --dataset default >> "$LOG" 2>&1 &
echo "PID: $!"
echo "Log: $PWD/$LOG"
echo "Tail: tail -f $PWD/$LOG"
