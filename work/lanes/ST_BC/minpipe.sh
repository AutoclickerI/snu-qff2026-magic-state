#!/bin/bash
# usage: minpipe.sh <stem relative to ST_BC, e.g. c_sat6_14_400_305>  -> picks measure-init sites lowering 2nd order, scores --third
cd /home/jihoon/competitions/quantumn/work/lanes/ST_BC
s=$1; mkdir -p mi/$s; P=../../../.venv/bin/python
sites=$($P ../MAIN/minit.py $s mi/$s | sed 's/sites \[\(.*\)\]/\1/;s/,//g')
base=$(cd ../.. && ../.venv/bin/python lanes/EVAL/exact2.py lanes/ST_BC/$s.qasm 2>&1 | grep -a '(2nd order)' | awk '{print $5}')
pick=""
for q in $sites; do
  v=$(cd ../.. && ../.venv/bin/python lanes/EVAL/exact2.py lanes/ST_BC/mi/$s/${s}_m$q.qasm 2>&1 | grep -a '(2nd order)' | awk '{print $5}')
  if python3 -c "import sys;sys.exit(0 if float('$v')<float('$base') else 1)"; then pick="$pick,$q"; fi
done
pick=${pick#,}
echo "$s base2nd=$base picked=$pick"
[ -z "$pick" ] && exit 0
$P ../MAIN/minit.py $s mi/$s $pick >/dev/null
f=mi/$s/${s}_m$(echo $pick | tr , _)
cd ../.. && ../.venv/bin/python lanes/EVAL/exact2.py lanes/ST_BC/$f.qasm --third 2>&1 | grep -aE 'first order|2nd|third|1-F \(to|exp'
echo "OUT $f"
