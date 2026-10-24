"""Run the unchanged exact2 CLI; confine caches and disable bytecode writes."""
import os,sys,runpy,json,hashlib,time,contextlib,fcntl
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
import xtim
xtim.cache_dir=str(H/'.xtim_cache')
sys.path.insert(0,str(ROOT/'work/lanes/EVAL'))
target=str(ROOT/'work/lanes/EVAL/exact2.py')
original=[target,*sys.argv[1:]]
# Optional priority cases run in this same process and worker allocation. No reference
# evaluator code changes, additional process pools, or interrupted evaluations.
while (H/'priority_reference.json').exists():
 with (H/'priority.lock').open('w') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX)
  queue=json.loads((H/'priority_reference.json').read_text())
  if not queue:break
  row=queue.pop(0);(H/'priority_reference.json').write_text(json.dumps(queue))
 stem=row['stem'];p=H/(stem+'.qasm');rc=H/(stem+'.ref.exit.json')
 sha=hashlib.sha256(p.read_bytes()).hexdigest()
 if rc.exists() and json.loads(rc.read_text()).get('sha256')==sha and json.loads(rc.read_text()).get('returncode')==0:continue
 procs=original[original.index('--procs')+1];start=time.monotonic()
 sys.argv=[target,str(p),'--third','--procs',procs,'--top','10','--json',str(H/(stem+'.ref.sensitivity.json'))]
 with (H/(stem+'.ref.log')).open('w') as f,contextlib.redirect_stdout(f),contextlib.redirect_stderr(f):
  runpy.run_path(target,run_name='__main__')
 rc.write_text(json.dumps(dict(stem=stem,returncode=0,seconds=time.monotonic()-start,sha256=sha,priority=True)))
sys.argv=original
runpy.run_path(target,run_name='__main__')
