"""Complete judge/FAST gates, then exec the unchanged three-seed MC harness."""
import os,sys,runpy,json,contextlib
from pathlib import Path
H=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1';os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
name=sys.argv[1];procs=sys.argv[2] if len(sys.argv)>2 else '7';sys.argv=[str(H/'gate.py'),name]
with (H/(name+'.gate.log')).open('w') as f,contextlib.redirect_stdout(f),contextlib.redirect_stderr(f):runpy.run_path(str(H/'gate.py'),run_name='__main__')
g=json.loads((H/(name+'.gate.json')).read_text());print('GATE',name,g,flush=True)
if not g.get('passed') or g.get('speed',{}).get('classification')!='FAST':raise SystemExit(2)
os.execv(sys.executable,[sys.executable,str(H/'mc3.py'),str(H/name),'--procs',procs])
