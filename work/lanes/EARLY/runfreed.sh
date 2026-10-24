#!/bin/bash
# usage: runfreed.sh R W prio label... ; runs freed.py per data label in parallel (WORKERS=8), waits for all
cd /home/jihoon/competitions/quantumn/work/lanes/EARLY
R=$1; W=$2; PR=$3; shift 3
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 WORKERS=8
for i in "$@"; do
  timeout 900 ../../../.venv/bin/python freed.py $R $W $i $PR > logs/freed_${R}_${W}_${i}_${PR}.log 2>&1 &
done
wait
cat logs/freed_${R}_${W}_*_${PR}.log 2>/dev/null | grep -v "^ \|^  " | head -0
for i in "$@"; do head -1 logs/freed_${R}_${W}_${i}_${PR}.log; done
