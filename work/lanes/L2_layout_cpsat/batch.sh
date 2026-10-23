#!/bin/bash
# usage: batch.sh <tag> <steps> <lmax> <chains> <seed0> <variant>...
tag=$1; steps=$2; lmax=$3; n=$4; s0=$5; shift 5
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for v in "$@"; do
  ../../../.venv/bin/python l2run.py "$v" $steps $lmax $n $s0 >> log_batch_$tag.txt 2>&1
  echo "DONE $v $lmax" >> log_batch_$tag.txt
done
echo ALLDONE >> log_batch_$tag.txt
