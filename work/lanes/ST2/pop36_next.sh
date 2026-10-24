#!/usr/bin/env bash
set -euo pipefail
cd /home/jihoon/competitions/quantumn
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
.venv/bin/python work/lanes/ST2/pop36_search.py zebra 7 360210 > work/lanes/ST2/pop36b/zebra.log 2>&1
