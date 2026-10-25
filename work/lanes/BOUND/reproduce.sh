#!/usr/bin/env bash
# Invoke on hippo; one single-thread Python process at a time.
set -euo pipefail
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd /home/jihoon/competitions/quantumn
if [[ $(hostname -s) != hippo ]]; then
    echo 'Run this script on hippo.' >&2
    exit 1
fi
lane=work/lanes/BOUND
for script in legacy_audit/terminal_bound.py legacy_audit/independent_matrix.py legacy_reviewer11/terminal_bound.py strengthened.py verify_certificate.py matrix_check.py; do
    .venv/bin/python -I "$lane/$script" > "$lane/${script%.py}.log"
done
cmp "$lane/legacy_audit/terminal_bound.json" "$lane/legacy_reviewer11/terminal_bound.json"
cat "$lane/verification.json" "$lane/matrix_check.log"
