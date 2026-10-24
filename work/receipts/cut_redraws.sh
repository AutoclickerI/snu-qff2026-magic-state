#!/bin/bash
# Usage: cut_redraws.sh <stem name> <time accepted by date -d, e.g. "00:20 tomorrow"> <host>...
# Stops the stem's re-draws at HHMM KST so promote.sh can pick the best completed draw in time for the next slot.
name=$1; t=$2; shift 2
SSH="ssh -q -o ControlMaster=no -o ControlPath=none"
target=$(date -d "$t" +%s) || exit 1; echo "cut at $(date -d @$target)"
until [ "$(date +%s)" -ge "$target" ]; do sleep 20; done
pat="reorder.py lanes\\/MAIN\\/${name:0:${#name}-1}[${name: -1}]"
for h in "$@"; do
  if [ "$h" = owl ]; then $SSH owl "docker ps --no-trunc --format '{{.ID}} {{.Command}}' | awk '/$pat/ {print substr(\$1,1,12)}' | xargs -r docker kill"
  else $SSH $h "ps -u jihoon -o pid,args | awk '/$pat/ {print \$1}' | xargs -r kill"; fi
done
date; echo cut
