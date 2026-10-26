#!/usr/bin/env bash
set -euo pipefail
cd /home/jihoon/competitions/quantumn
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
.venv/bin/python -B -u work/lanes/MERGE/wide5.py "${1:-10}" 2>&1 | tee -a work/lanes/MERGE/res37h/run.log
