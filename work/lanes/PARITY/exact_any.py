"""exact2.py with the adjacency rule off: ceilings of gadgets that ignore the grid (not submittable)."""
import os
for _v in ("OMP_NUM_THREADS","OPENBLAS_NUM_THREADS","MKL_NUM_THREADS"): os.environ[_v]="1"
import sys, runpy
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/EVAL")
import tprep.qasm as tq
tq.adjacent = lambda a, b: True
sys.argv[0] = "/home/jihoon/competitions/quantumn/work/lanes/EVAL/exact2.py"
runpy.run_path(sys.argv[0], run_name="__main__")
