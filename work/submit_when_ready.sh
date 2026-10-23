#!/bin/bash
# Usage: submit_when_ready.sh <stem>
# Waits until 3605 s after our last server-side submission (from `submit.py status`) and for the stem's
# receipts/seq_<name>.txt, then submits only if the sequential judge printed RESULT: PASS. Prints DONE.
cd /home/jihoon/competitions/quantumn/work
PY=/home/jihoon/competitions/quantumn/.venv/bin/python
stem=$1; rec=receipts/seq_$(basename $stem).txt
last=$(timeout 60 $PY submit.py status | $PY -c "
import sys, json, datetime
t = sys.stdin.read(); t = t[t.index('['):]
rows = json.loads(t)
print(max(int(datetime.datetime.fromisoformat(r['submitted_at']).timestamp()) for r in rows))")
target=$((last + 3605)); echo "last submission $(date -d @$last +%T), submitting after $(date -d @$target +%T)"
until [ "$(date +%s)" -ge "$target" ]; do sleep 5; done
until grep -q "c1 ~" "$rec" 2>/dev/null || grep -q "Traceback" "$rec" 2>/dev/null; do sleep 5; done
if grep -q "RESULT: PASS" "$rec"; then date; timeout 120 $PY submit.py submit $stem.qasm $stem.json
else echo "sequential check did not pass; not submitted"; fi
echo DONE
