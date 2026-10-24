import os,sys,json,re,subprocess,time,hashlib,argparse
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parents[1]));os.chdir(H)
import tprep,fast_check,xtim
xtim.cache_dir=str(H/'.xtim_cache')
p=argparse.ArgumentParser();p.add_argument('stem');p.add_argument('--procs',type=int,default=6);p.add_argument('--force-mc',action='store_true');a=p.parse_args()
stem=Path(a.stem).resolve();assert stem.is_relative_to(H)
txt=stem.with_suffix('.qasm').read_text();d=json.loads(stem.with_suffix('.json').read_text());out=dict(sha256=hashlib.sha256(txt.encode()).hexdigest(),metadata=d)
def save():Path(str(stem)+'.score.json').write_text(json.dumps(out,indent=2)+'\n')
r=tprep.check(txt,d['data_qubits'],shots=10**6,seed=0);Path(str(stem)+'.check.log').write_text(str(r)+'\n');out.update(judge_passed=r.passed,correct_ok=r.correct_ok,acceptance_1e6=r.acceptance);save();print(r,flush=True)
if not r.correct_ok:sys.exit(0)
cmd=[sys.executable,str(H.parent/'EVAL/exact2.py'),str(stem)+'.qasm','--third','--procs',str(a.procs),'--top','0','--json',str(stem)+'.exact.json']
p=subprocess.run(cmd,capture_output=True,text=True)
Path(str(stem)+'.exact.log').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)
if p.returncode:raise RuntimeError(p.stderr)
for k,pat in [('c1',r'c1 p = ([\deE+.\-]+)'),('second',r'1-F \(2nd order\) = ([\deE+.\-]+)'),('third',r'third order: ([\deE+.\-]+)'),('total',r'1-F \(to 3rd order\) = ([\deE+.\-]+)'),('exp_A1',r'exp\(-A1\) = ([\deE+.\-]+)')]:
 m=re.search(pat,p.stdout)
 if m:out[k]=float(m.group(1))
save()
if a.force_mc or abs(out.get('c1',1))>=1e-12 or out.get('total',1)<8.6e-5:
 out['mc']=[]
 for seed in (0,1000,2000):
  # Capacity receipt before every multiprocessing launch.
  print('launch',seed,'cores',os.cpu_count(),'load',Path('/proc/loadavg').read_text().strip(),flush=True)
  r=fast_check.check(txt,d['data_qubits'],shots=10**8,seed=seed,procs=a.procs);out['mc'].append(dict(seed=seed,score=r.score,acceptance=r.acceptance,sem=r.sem,passed=r.passed));save();print('MC',out['mc'][-1],flush=True)
 out['mean']=sum(x['score'] for x in out['mc'])/3;save()
