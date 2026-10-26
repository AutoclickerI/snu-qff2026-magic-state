cd /home/jihoon/competitions/quantumn/work
PY=/home/jihoon/competitions/quantumn/.venv/bin/python
stem=$1; rec=receipts/seq_$(basename $stem).txt
grep -q "RESULT: PASS" "$rec" 2>/dev/null || { echo "sequential check did not pass; not submitted"; echo DONE; exit 1; }
# Submit only a draw whose key (3 significant figures) is below our board key: an equal or worse key cannot change the
# board, and skipping it frees the slot for a finalist and resets the cooldown phase (each submission drifts it ~8 s).
score=$(sed -n 's/.*score 1-F = \([0-9.e+-]*\).*/\1/p' "$rec" | head -1)
board=$(timeout 60 $PY submit.py key 2>/dev/null | tail -1)
python3 -c "
import sys
s = float(f'{float(sys.argv[1]):.2e}')
try: b = float(sys.argv[2]) if float(sys.argv[2]) > 0 else float('inf')  # board unreadable: submit
except ValueError: b = float('inf')
sys.exit(0 if s < b else 1)" "$score" "$board" \
  || { echo "key of $score does not beat board key $board; not submitted"; echo DONE; exit 0; }
exec 9>receipts/.submit.lock; flock 9
w=$(timeout 60 $PY submit.py wait)
until [ "${w:--1}" -ge 0 ] 2>/dev/null; do sleep 30; w=$(timeout 60 $PY submit.py wait); done
target=$(( $(date +%s) + w + 5 )); echo "server wait ${w}s, submitting after $(date -d @$target +%T)"
until [ "$(date +%s)" -ge "$target" ]; do sleep 5; done
date; timeout 120 $PY submit.py submit $stem.qasm $stem.json
echo DONE
