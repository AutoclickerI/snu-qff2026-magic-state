#!/bin/bash
# soft Z-weighted synthesis -> proxy LNS on v36d:  pipe.sh <tag> <synth seed> <wz> <synth s> <lns s> <lns seed>...
# outputs syn/<tag>.json (synthesis), syn/<tag>_l<seed>.json/.log (LNS best)
cd /home/jihoon/competitions/quantumn/work/lanes/BFLAG
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
P=../../../.venv/bin/python
tag=$1; seed=$2; wz=$3; ss=$4; ls=$5; shift 5
$P synth_bc.py --base v36d --soft 50,20 --wz $wz --wcx 12 --D 11 --T0 33 --seed $seed --seconds $ss --workers 2 --out syn/$tag.json > syn/$tag.log 2>&1
for s in "$@"; do
  BFLAG_BASE=v36d $P lns3.py syn/$tag.json syn/${tag}_l$s $ls $s - 1.1e-4 3e-5 > syn/${tag}_l$s.log 2>&1 &
done
wait
