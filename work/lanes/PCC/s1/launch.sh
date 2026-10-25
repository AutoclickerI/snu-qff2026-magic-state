#!/bin/bash
# launch stage-1 workers on this host: launch.sh <nworkers> <procs each>
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
cd /home/jihoon/competitions/quantumn/work/lanes/PCC/ev || exit 1
for i in $(seq 0 $(($1-1))); do
  nohup /home/jihoon/competitions/quantumn/.venv/bin/python ../stage1.py run $i $1 $2 > ../s1/worker_$i.log 2>&1 &
  echo $! > ../s1/worker_$i.pid
done
cat ../s1/worker_*.pid
