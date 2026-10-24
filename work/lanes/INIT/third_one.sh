#!/bin/bash
set -e
name="$1"
/home/jihoon/competitions/quantumn/.venv/bin/python work/lanes/EVAL/exact2.py "work/lanes/INIT/${name}.qasm" --data "work/lanes/INIT/${name}.json" --procs 4 --top 0 --third > "work/lanes/INIT/${name}.third.log" 2>&1
