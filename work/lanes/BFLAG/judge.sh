#!/bin/bash
# judge.sh <host> <stem relative to BFLAG>: official 1e6 check (8 procs) + speed probe, run on <host>
h=$1; s=$2
cd /home/jihoon/competitions/quantumn/work/lanes/BFLAG
rsync -a -e "ssh -q -o ControlMaster=no -o ControlPath=none" --relative ./$s.qasm ./$s.json $h:/home/jihoon/competitions/quantumn/work/lanes/BFLAG/
ssh -q -o ControlMaster=no -o ControlPath=none $h "cd /home/jihoon/competitions/quantumn/work; export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1; ../.venv/bin/python fast_check.py lanes/BFLAG/$s.qasm lanes/BFLAG/$s.json 1000000 8 2>&1 | tail -2; ../.venv/bin/python lanes/XTIM/speed_predict.py lanes/BFLAG/$s 2>&1 | tail -1 | cut -c1-400"
