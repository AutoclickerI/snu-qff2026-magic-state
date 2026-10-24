"""Run unchanged requested mc3.py with cache constrained to this lane."""
import os,sys,runpy
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
os.environ['XTIM_TWIRL_CACHE_DIR']=str(OUT/'.xtim_cache');os.environ['PYTHONDONTWRITEBYTECODE']='1';sys.dont_write_bytecode=True
for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS']:os.environ[key]='1'
import xtim
xtim.cache_dir=str(OUT/'.xtim_cache')
runpy.run_path(str(OUT/'inputs/mc3.py'),run_name='__main__')
