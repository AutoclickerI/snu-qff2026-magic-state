"""Run unchanged exact2 with only its detector-mask storage widened beyond int64."""
import os,sys,runpy
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path[:0]=[str(H/'r35_exact'),str(ROOT/'upstream/snu-qff2026-problem')]
import xtim
xtim.cache_dir=str(H/'r35/.xtim_cache');os.environ['XTIM_TWIRL_CACHE_DIR']=xtim.cache_dir
import engine
# A representation fix: arithmetic, projection order, coefficients and evaluator unchanged.
src=(H/'r35_exact/engine.py').read_text();a=src.index('def batch_tables(');b=src.index('\ndef batch_n(',a)
code=src[a:b].replace('D = np.asarray(D, dtype=np.int64)','D = np.asarray(D, dtype=object)')
exec(compile(code,str(H/'r35_exact/engine.py')+':wide','exec'),engine.__dict__)
engine.Engine.batch_tables=engine.batch_tables
sys.argv=[str(H/'r35_exact/exact2.py'),*sys.argv[1:]]
runpy.run_path(sys.argv[0],run_name='__main__')
