#!/bin/bash
cd /home/jihoon/competitions/quantumn/work/lanes/ST_BC
f=$1; n=$(basename $f .json)
../../../.venv/bin/python check7.py $f
../../../.venv/bin/python ft.py $f | head -1
../../../.venv/bin/python rep.py $f | tail -1
cd ../DR && ../../../.venv/bin/python ../ST_BC/merge7.py L5 "a=prepA_L5_s7307.json,bc=../ST_BC/$f" ../ST_BC/c_$n a,bc 2>&1 | tail -1
cd ../.. && ../.venv/bin/python lanes/EVAL/exact2.py lanes/ST_BC/c_$n.qasm --third 2>&1 | grep -aE 'first order|2nd|third|1-F|acceptance:'
