#!/bin/bash
# push the evaluator, incumbent and this lane to a mirrored host (no --delete; lane dir only overwritten by us)
h=$1
cd /home/jihoon/competitions/quantumn
rsync -a -e "ssh -q" --relative work/lanes/MAIN/sparse work/lanes/MAIN/v36c.qasm work/lanes/MAIN/v36c.json work/lanes/BFLAG work/lanes/T14 work/lanes/XTIM work/fast_check.py work/lanes/EVAL $h:/home/jihoon/competitions/quantumn/ 
