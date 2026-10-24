#!/bin/bash
# all-orders on owl (docker, glibc): ao_owl.sh <procs> <stem>...  (stems relative to BFLAG, no suffix)
p=$1; shift 1
cd /home/jihoon/competitions/quantumn/work/lanes/BFLAG
rsync -a -e "ssh -q -o ControlMaster=no -o ControlPath=none" --relative ./sparse/aorun.py $(for s in "$@"; do echo ./$s.qasm ./$s.json; done) owl:/home/jihoon/competitions/quantumn/work/lanes/BFLAG/
args=$(for s in "$@"; do echo -n "../$s "; done)
ssh -q -o ControlMaster=no -o ControlPath=none owl "docker run --rm -u 1010:1012 -e HOME=/home/jihoon -e OMP_NUM_THREADS=1 -e OPENBLAS_NUM_THREADS=1 -e MKL_NUM_THREADS=1 -v /home/jihoon:/home/jihoon -w /home/jihoon/competitions/quantumn/work/lanes/BFLAG/sparse --cpus=$p fnc-build:22.04 /home/jihoon/competitions/quantumn/.venv/bin/python aorun.py $p $args" 2>&1 | grep -v cad.sh
