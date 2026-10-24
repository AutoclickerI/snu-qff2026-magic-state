#!/bin/bash
set -eu
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
for stem in work/lanes/MAIN/v35b work/lanes/FRESH/r35/sx_full work/lanes/MAIN/v24 work/lanes/XTIM/q8_reuse_v25k; do
 name=${stem##*/}
 TRACE_OUT=work/lanes/FRESH/r36/$name.trace.json gdb -q -batch -x work/lanes/FRESH/r36_trace.gdb --args .venv/bin/python -B work/lanes/FRESH/r36_probe.py "$stem" 1000 --exact-only > work/lanes/FRESH/r36/$name.trace.log 2>&1
 QEC_FRAMED_MEMO=0 .venv/bin/python -B work/lanes/FRESH/r36_probe.py "$stem" 10000 > work/lanes/FRESH/r36/$name.memo0.log 2>&1
 QEC_FORCE_FALLBACK=1 .venv/bin/python -B work/lanes/FRESH/r36_probe.py "$stem" 10000 > work/lanes/FRESH/r36/$name.fallback.log 2>&1
done
