#!/bin/bash
# all-orders of local stems on a remote host: ao.sh <host> <procs> <stem>...  (stems relative to BFLAG, no suffix)
h=$1; p=$2; shift 2
cd /home/jihoon/competitions/quantumn/work/lanes/BFLAG
rsync -a -e "ssh -q" --relative ./sparse/aorun.py $(for s in "$@"; do echo ./$s.qasm ./$s.json; done) $h:/home/jihoon/competitions/quantumn/work/lanes/BFLAG/
args=$(for s in "$@"; do echo -n "../$s "; done)
ssh -q $h "cd /home/jihoon/competitions/quantumn/work/lanes/BFLAG/sparse; export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1; ../../../../.venv/bin/python aorun.py $p $args"
