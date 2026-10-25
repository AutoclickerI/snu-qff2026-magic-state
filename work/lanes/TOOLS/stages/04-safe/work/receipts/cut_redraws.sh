#!/bin/bash
# Usage: cut_redraws.sh <stem name> <deadline accepted by date -d> <host>...
# Require patched race.py's registered controller. SIGUSR1 stops after complete chunks.
set -eu
name=$1; t=$2; shift 2
R=/home/jihoon/competitions/quantumn
PY=$R/.venv/bin/python
SSH="ssh -q -o ControlMaster=no -o ControlPath=none"
target=$(date -d "$t" +%s)
remaining=$((target - $(date +%s)))
if [ "$remaining" -gt 0 ]; then sleep "$remaining"; fi
for h in "$@"; do
  if [ "$h" = zebra ]; then
    "$PY" "$R/work/race_control.py" "$R/work/reorder/$name.pid.json"
  else
    # Owl races must use --pid=host; the controller uses only the standard library.
    $SSH "$h" "$PY $R/work/race_control.py $R/work/reorder/$name.pid.json"
  fi
done
date; echo 'cut: all registered controllers exited after checkpointing'
