"""Unmodified sparse evaluator, relocated only to keep its output in COMP29."""
import os,sys,json,time,hashlib,fcntl,traceback
from pathlib import Path
H=Path(__file__).resolve().parent
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.path.insert(0,str(H/'sparse35'))
import sparse_walsh as w
name=sys.argv[1];procs=int(sys.argv[2]) if len(sys.argv)>2 else 1
def evaluate(n):
    p=H/n;start=time.monotonic();sha=hashlib.sha256(p.with_suffix('.qasm').read_bytes()).hexdigest()
    try:r=w.run(p,72,True,procs);r.update(source_sha256=sha,validated=True)
    except Exception as e:
        r=dict(error=repr(e),seconds=time.monotonic()-start,source_sha256=sha);traceback.print_exc()
    tmp=p.with_suffix('.allorders.json.tmp');tmp.write_text(json.dumps(r,indent=2)+'\n');os.replace(tmp,p.with_suffix('.allorders.json'));return r
priority=H/'priority35.json'
if priority.exists():
    import contextlib
    for n in json.loads(priority.read_text()):
        if n==name or (H/(n+'.allorders.json')).exists():continue
        lock=(H/(n+'.priority.lock')).open('a+')
        try:fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:lock.close();continue
        if (H/(n+'.allorders.json')).exists():lock.close();continue
        with (H/(n+'.allorders.log')).open('w') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):r=evaluate(n)
        print('PRIORITY COMPLETE',n,r.get('loss'),r.get('error'),flush=True);lock.close()
r=evaluate(name)
if 'error' in r:raise SystemExit(1)
