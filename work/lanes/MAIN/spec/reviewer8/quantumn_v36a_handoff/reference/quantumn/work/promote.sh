#!/bin/bash
# Usage: promote.sh <stem> <host:procs:first:count>...   (host "zebra" runs here; "owl" runs through docker)
# Seed-0 re-draws of <stem> (reorder.py) spread over hosts; the best passing draw by seed-0 1-F is copied to
# submissions/, checked by the sequential judge, committed and pushed, then submitted at the next slot by
# submit_when_ready.sh. Re-draw variant numbers must not overlap between hosts.
set -u
R=/home/jihoon/competitions/quantumn
cd $R/work
PY=$R/.venv/bin/python
ENV="OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1"
SSH="ssh -q -o ControlMaster=no -o ControlPath=none"
stem=$1; shift
name=$(basename "$stem"); dir=$(dirname "$stem")
# Server time limit (CONSTRAINTS rule 5): refuse a candidate whose single-process 1e6-shot judge run exceeds 20 s.
s=$(date +%s.%N); env $ENV $PY fast_check.py "$stem.qasm" "$stem.json" 1000000 1 > /dev/null 2>&1; e=$(date +%s.%N)
secs=$(python3 -c "print(round($e - $s, 1))"); echo "judge speed: $secs s per 1e6 shots, 1 process"
python3 -c "import sys; sys.exit(0 if $secs <= 20 else 1)" || { echo "too slow for the server's 1-hour limit; not promoted"; exit 1; }
pids=()
for spec in "$@"; do
  IFS=: read -r h procs first count <<< "$spec"
  log=reorder/${name}_$h.log
  run="$PY reorder.py $stem $count $procs $first"
  if [ "$h" = zebra ]; then
    env $ENV nice -n 5 $run > "$log" 2>&1 &
  else
    $SSH "$h" "mkdir -p $R/work/$dir $R/work/reorder" 2>/dev/null && rsync -a -e "$SSH" "$stem.qasm" "$stem.json" "$h:$R/work/$dir/"
    if [ "$h" = owl ]; then
      run="docker run --rm -u 1010:1012 -e HOME=/home/jihoon -e OMP_NUM_THREADS=1 -e OPENBLAS_NUM_THREADS=1 -e MKL_NUM_THREADS=1 -v /home/jihoon:/home/jihoon -w $R/work --cpus=$procs fnc-build:22.04 $run"
    else
      run="env $ENV nice -n 5 $run"
    fi
    $SSH "$h" "cd $R/work; $run" > "$log" 2>&1 &
  fi
  pids+=($!)
done
wait "${pids[@]}"
for spec in "$@"; do
  h=${spec%%:*}
  [ "$h" = zebra ] || rsync -a -e "$SSH" "$h:$R/work/reorder/${name}_r*" reorder/
done
best=$(cat reorder/${name}_*.log | awk '$2 == "1-F" && $NF == "True" {print $3, $1}' | sort -g | head -1)
echo "best re-draw: $best ($(cat reorder/${name}_*.log | awk '$2 == "1-F" && $NF == "True"' | wc -l) passing draws)"
pick=${best#* }
[ -n "$pick" ] || { echo "no passing re-draw"; exit 1; }
cp reorder/$pick.qasm reorder/$pick.json submissions/
env OMP_NUM_THREADS=4 timeout 1500 $PY seqcheck.py submissions/$pick > receipts/seq_$pick.txt 2>&1
grep -E "RESULT|score 1-F" receipts/seq_$pick.txt
grep -q "RESULT: PASS" receipts/seq_$pick.txt || { echo "sequential judge did not pass"; exit 1; }
cd $R
git add work/submissions/$pick.qasm work/submissions/$pick.json work/receipts/seq_$pick.txt
PW=$(sed -n 's/^PASSWORD=//p' .submit_credentials)
if [ "$(git diff --cached | grep -cF -- "$PW")" != 0 ]; then echo "password in the staged diff; not committed"; exit 1; fi
git commit -q -m "submission candidate $pick (best of the re-draws of $name)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -- work/submissions/$pick.qasm work/submissions/$pick.json work/receipts/seq_$pick.txt
git push -q origin main
cd $R/work
bash submit_when_ready.sh submissions/$pick 2>&1 | tee receipts/submit_$pick.log | tail -3
