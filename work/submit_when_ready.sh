#!/bin/bash
# Usage: submit_when_ready.sh <stem>
# Waits for the server's cooldown (`submit.py wait`, +5 s) and for the stem's
# receipts/seq_<name>.txt, then submits only if the sequential judge printed RESULT: PASS. Prints DONE.
# Concurrent callers queue on a lock, so each one takes its own slot.
cd /home/jihoon/competitions/quantumn/work
exec 9>receipts/.submit.lock; flock 9
PY=/home/jihoon/competitions/quantumn/.venv/bin/python
stem=$1; rec=receipts/seq_$(basename $stem).txt
w=$(timeout 60 $PY submit.py wait)
until [ "${w:--1}" -ge 0 ] 2>/dev/null; do sleep 30; w=$(timeout 60 $PY submit.py wait); done
target=$(( $(date +%s) + w + 5 )); echo "server wait ${w}s, submitting after $(date -d @$target +%T)"
until [ "$(date +%s)" -ge "$target" ]; do sleep 5; done
until grep -q "c1 ~" "$rec" 2>/dev/null || grep -q "Traceback" "$rec" 2>/dev/null; do sleep 5; done
if grep -q "RESULT: PASS" "$rec"; then date; timeout 120 $PY submit.py submit $stem.qasm $stem.json
else echo "sequential check did not pass; not submitted"; fi
echo DONE
