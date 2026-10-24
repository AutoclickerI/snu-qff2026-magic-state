#!/bin/bash
# run_syn.sh <tag> <args...>   (runs on the current host, writes syn/<tag>.json and syn/<tag>.log)
cd /home/jihoon/competitions/quantumn/work/lanes/BFLAG
tag=$1; shift
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
nice -n 5 ../../../.venv/bin/python synth_bc.py "$@" --out syn/$tag.json > syn/$tag.log 2>&1
