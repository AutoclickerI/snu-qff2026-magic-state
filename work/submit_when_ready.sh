#!/bin/bash
# Usage: submit_when_ready.sh <stem> <HH:MM:SS today> ; waits for the slot and for the stem's seqcheck receipt,
# submits only if the sequential judge printed RESULT: PASS. Prints DONE at the end.
cd /home/jihoon/competitions/quantumn/work
stem=$1; at=$2; rec=receipts/seq_$(basename $stem).txt
target=$(date -d "$(date +%F) $at" +%s)
until [ "$(date +%s)" -ge "$target" ]; do sleep 5; done
until grep -q "c1 ~" "$rec" 2>/dev/null || grep -q "Traceback" "$rec" 2>/dev/null; do sleep 5; done
if grep -q "RESULT: PASS" "$rec"; then date; timeout 120 /home/jihoon/competitions/quantumn/.venv/bin/python submit.py submit $stem.qasm $stem.json
else echo "sequential check did not pass; not submitted"; fi
echo DONE
