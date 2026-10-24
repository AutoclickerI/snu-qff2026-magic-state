#!/bin/bash
set -e
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
exec /home/jihoon/competitions/quantumn/.venv/bin/python work/lanes/BUDGET/run_init_eval.py "$@"
