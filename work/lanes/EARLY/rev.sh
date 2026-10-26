#!/bin/bash
# Remote all-orders evaluation: rev.sh <host> <stem relative to EARLY> [procs]
# Syncs the lane dir (and judge upstream if missing), runs sparse_walsh there, prints the summary line.
h=$1; stem=$2; procs=${3:-16}
L=/home/jihoon/competitions/quantumn/work/lanes/EARLY
rsync -a --exclude 'sparse/*_sparse_result.json' $L/ $h:$L/ 2>/dev/null
ssh -q $h "cd /home/jihoon/competitions/quantumn/work/lanes/MAIN/sparse && OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 nice -n 5 ../../../../.venv/bin/python sparse_walsh.py ../../EARLY/$stem 72 canonical $procs 2>&1 | tail -1"
