"""Run the requested MAIN/spec/mc3.py unchanged, with all writes lane-local."""
import os
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from pathlib import Path
import sys
import runpy
import xtim
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
xtim.cache_dir=HERE/'.xtim_cache'
sys.argv=[str(HERE/'inputs/mc3.py')]+[str(HERE/n) for n in ('grid_v17a','grid_ac','grid_ac_only','grid_ac_aa')]+['--procs',sys.argv[1] if len(sys.argv)>1 else '24']
runpy.run_path(sys.argv[0],run_name='__main__')
