#!/bin/bash
cd /home/jihoon/competitions/quantumn/work/lanes/ST_BC
while true; do
 f=$(./wait.sh 2>/dev/null | grep -a NEW | awk '{print $2}')
 [ -z "$f" ] && continue
 { echo "=== $f $(../../../.venv/bin/python rep.py $f | tail -1)"; ./proc.sh $f 2>&1 | grep -aE 'True|False|bad|first order|2nd|third|1-F \(to|exp';   ./minpipe.sh c_$(basename $f .json) 2>&1 | grep -aE 'picked|1-F \(to|OUT'; } >> results.txt
done
