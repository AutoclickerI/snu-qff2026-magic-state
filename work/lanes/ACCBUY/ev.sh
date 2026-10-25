#!/bin/bash
# usage: ev.sh <abs stem> [procs]  -> prints loss acceptance
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
P=${2:-8}
cd ${EVD:-/home/jihoon/competitions/quantumn/work/lanes/ACCBUY/sparse}
../../../../.venv/bin/python sparse_walsh.py "$1" 72 canonical $P 2>&1 | tail -1 | python3 -c "
import sys,json
l=sys.stdin.read()
try:
  d=json.loads(l); print('$1'.split('/')[-1], repr(d['loss']), d['acceptance'], round(d['seconds'],1))
except Exception as e: print('$1'.split('/')[-1], 'ERR', l[:300])
"
