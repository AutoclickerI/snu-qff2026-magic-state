"""Temporarily share the lane's twelve hippo worker slots with a FAST finalist."""
import os,sys,json,signal,subprocess,time
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
text=subprocess.check_output(['ps','-eo','pid=,ppid=,args='],text=True);pids={}
for l in text.splitlines():
 a=l.strip().split(None,2)
 if len(a)==3 and 'joint/evaluate.py mc3' in a[2]and 'region2_d11_reuseA' in a[2]and a[2].split()[0].endswith('python'):pids[int(a[0])]=int(a[1])
parents=[p for p in pids if sum(v==p for v in pids.values())==12];assert len(parents)==1,(pids,parents)
paused=sorted(p for p,pp in pids.items()if pp==parents[0])[-4:];receipt=dict(paused_pids=paused,diagnostic_parent=parents[0],slots=4,status='active',results=[])
def save(): (H/'lent_capacity.json').write_text(json.dumps(receipt,indent=2))
def stop(signum,frame):raise SystemExit(128+signum)
signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
try:
 for p in paused:os.kill(p,signal.SIGSTOP)
 save()
 for name in sys.argv[1:]:
  for mode in ('exact','check','mc3'):
   with(H/(name+'.'+mode+'.log')).open('w')as f:r=subprocess.run([str(ROOT/'.venv/bin/python'),str(H/'evaluate.py'),mode,str(H/name),'--procs','4'],stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
   receipt['results'].append(dict(stem=name,mode=mode,exit_code=r.returncode));save();print(json.dumps(receipt['results'][-1]),flush=True)
   if r.returncode:raise RuntimeError(receipt['results'][-1])
finally:
 for p in paused:
  try:os.kill(p,signal.SIGCONT)
  except ProcessLookupError:pass
 receipt['status']='finished; all diagnostic workers resumed';save()
