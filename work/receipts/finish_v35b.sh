#!/bin/bash
# Tail of promote.sh for v35b after its re-draws were stopped early: best draw -> seqcheck -> commit -> push -> submit.
set -u
R=/home/jihoon/competitions/quantumn; cd $R/work; PY=$R/.venv/bin/python; pick=v35b_r1007
cp reorder/$pick.qasm reorder/$pick.json submissions/
env OMP_NUM_THREADS=4 timeout 1500 $PY seqcheck.py submissions/$pick > receipts/seq_$pick.txt 2>&1
grep -E "RESULT|score 1-F" receipts/seq_$pick.txt
grep -q "RESULT: PASS" receipts/seq_$pick.txt || { echo "sequential judge did not pass"; exit 1; }
cd $R; git add work/submissions/$pick.qasm work/submissions/$pick.json work/receipts/seq_$pick.txt
PW=$(sed -n 's/^PASSWORD=//p' .submit_credentials)
if [ "$(git diff --cached | grep -cF -- "$PW")" != 0 ]; then echo "password in the staged diff; not committed"; exit 1; fi
git commit -q -m "submission candidate $pick (best of 606 re-draws of v35b)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- work/submissions/$pick.qasm work/submissions/$pick.json work/receipts/seq_$pick.txt
git push -q origin main
cd $R/work; bash submit_when_ready.sh submissions/$pick 2>&1 | tee receipts/submit_$pick.log | tail -3
