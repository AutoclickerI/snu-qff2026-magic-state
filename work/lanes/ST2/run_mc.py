import os,sys,runpy
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
import xtim
xtim.cache_dir=str(H/'.xtim_cache')
path=H/'mc3.py'  # byte-identical portable copy of MAIN/spec/mc3.py
sys.argv=[str(path),*sys.argv[1:]]
runpy.run_path(str(path),run_name='__main__')
