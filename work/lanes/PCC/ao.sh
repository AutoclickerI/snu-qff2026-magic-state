#!/bin/bash
# usage: ao.sh <evaluator: main|s40> <abs stem> <procs> <logname>
# launches the all-orders evaluator in the background, writes runs/<logname>.pid and runs/<logname>.log
set -u
L=/home/jihoon/competitions/quantumn/work/lanes
case "$1" in main) E=$L/MAIN/sparse;; s40) E=$L/ACCBUY/sparse40;; pcc) E=$L/PCC/ev;; *) echo bad; exit 1;; esac
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd "$E" || exit 1
nohup /home/jihoon/competitions/quantumn/.venv/bin/python sparse_walsh.py "$2" 72 canonical "$3" > "$L/PCC/runs/$4.log" 2>&1 &
echo $! > "$L/PCC/runs/$4.pid"
echo $!
