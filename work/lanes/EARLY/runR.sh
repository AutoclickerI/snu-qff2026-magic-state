#!/bin/bash
# usage: runR.sh W prio R... ; freed.py at several R in parallel (WORKERS=8), no required data
cd /home/jihoon/competitions/quantumn/work/lanes/EARLY
W=$1; PR=$2; shift 2
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 WORKERS=8
for R in "$@"; do timeout 900 ../../../.venv/bin/python freed.py $R $W - $PR > logs/freedR_${R}_${W}_${PR}.log 2>&1 & done
wait
for R in "$@"; do cat logs/freedR_${R}_${W}_${PR}.log; done
