#!/bin/bash
# wait for the stage-1 workers (PIDs in worker_*.pid), then run batch 2 with 3 workers x 8 processes
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
D=/home/jihoon/competitions/quantumn/work/lanes/PCC/s1
for f in $D/worker_0.pid $D/worker_1.pid $D/worker_2.pid; do p=$(cat $f); while kill -0 $p 2>/dev/null; do sleep 3; done; done
cd /home/jihoon/competitions/quantumn/work/lanes/PCC/ev || exit 1
for i in 0 1 2; do
  /home/jihoon/competitions/quantumn/.venv/bin/python ../stage1.py run2 $i 3 8 > $D/worker2_$i.log 2>&1 &
  echo $! > $D/worker2_$i.pid
done
wait
