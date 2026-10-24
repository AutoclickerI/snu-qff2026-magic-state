"""Official judge, unchanged XTIM probe and MAIN three-seed MC; lane-local receipts."""
import os,sys,json,time,hashlib,runpy,contextlib,re
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;V=H/'v35';ROOT=H.parents[2]
os.environ['XTIM_TWIRL_CACHE_DIR']=str(V/'.xtim_cache')
sys.path[:0]=[str(H),str(ROOT/'work')]
import fast_check,xtim,v35_speed
xtim.cache_dir=str(V/'.xtim_cache')
def gate(name):
 p=V/name;text=p.with_suffix('.qasm').read_text();md=json.loads(p.with_suffix('.json').read_text())
 speed=v35_speed.predict(str(p));g=dict(stem=name,speed=speed,passed=False,sha256=hashlib.sha256(text.encode()).hexdigest(),host=os.uname().nodename)
 if speed['classification']=='FAST':
  start=time.monotonic();r=fast_check.check(text,md['data_qubits'],shots=10**6,seed=0,procs=1)
  g.update(passed=r.passed,format=r.format_ok,correctness=r.correct_ok,acceptance=r.acceptance,score=float(r.score)if r.score is not None else None,sem=float(r.sem)if r.sem is not None else None,cx=r.n_2q,seconds=time.monotonic()-start)
  p.with_suffix('.judge.log').write_text(str(r)+'\n')
 p.with_suffix('.gates.json').write_text(json.dumps(g,indent=2)+'\n');print(json.dumps(g),flush=True)
 return g
def mc(name,procs):
 p=V/name;start=time.monotonic();log=p.with_suffix('.mc3.log');old=sys.argv;sys.argv=['mc3.py',str(p),'--procs',str(procs)]
 try:
  with log.open('w')as f,contextlib.redirect_stdout(f),contextlib.redirect_stderr(f):runpy.run_path(str(H/'v35_mc3.py'),run_name='__main__')
 finally:sys.argv=old
 ss=[dict(seed=int(seed),score=float(score),sem=float(sem),acceptance=float(acc))for seed,score,sem,acc in re.findall(r' (0|1000|2000) ([0-9.e+-]+) ± ([0-9.e+-]+) acc ([0-9.]+)',log.read_text())]
 assert len(ss)==3
 r=dict(stem=name,seeds=ss,mean=sum(x['score']for x in ss)/3,mean_sem=sum(x['sem']**2 for x in ss)**.5/3,returncode=0,sha256=hashlib.sha256(p.with_suffix('.qasm').read_bytes()).hexdigest(),procs=procs,seconds=time.monotonic()-start)
 p.with_suffix('.mc.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
if __name__=='__main__':
 mode=sys.argv[1];name=sys.argv[2]
 if mode=='gate':gate(name)
 elif mode=='mc':mc(name,int(sys.argv[3]))
