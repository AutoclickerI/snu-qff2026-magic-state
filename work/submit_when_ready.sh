#!/bin/bash
# Usage: submit_when_ready.sh <stem>
# promote.sh calls this after the sequential judge (seqcheck.py) has exited. Submits only if its receipt
# receipts/seq_<name>.txt says RESULT: PASS, waiting for the server's cooldown (`submit.py wait`, +5 s). Prints DONE.
# Concurrent callers queue on a lock held only for the cooldown wait and the submission.
cd /home/jihoon/competitions/quantumn/work
PY=/home/jihoon/competitions/quantumn/.venv/bin/python
stem=$1; rec=receipts/seq_$(basename $stem).txt
grep -q "RESULT: PASS" "$rec" 2>/dev/null || { echo "sequential check did not pass; not submitted"; echo DONE; exit 1; }
exec 9>receipts/.submit.lock; flock 9
w=$(timeout 60 $PY submit.py wait)
until [ "${w:--1}" -ge 0 ] 2>/dev/null; do sleep 30; w=$(timeout 60 $PY submit.py wait); done
target=$(( $(date +%s) + w + 5 )); echo "server wait ${w}s, submitting after $(date -d @$target +%T)"
until [ "$(date +%s)" -ge "$target" ]; do sleep 5; done
date; timeout 120 $PY submit.py submit $stem.qasm $stem.json
echo DONE
