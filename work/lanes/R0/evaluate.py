import os,sys,json,re,subprocess,time,hashlib
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent;os.chdir(H);sys.path.insert(0,str(H.parents[1]))
import tprep,fast_check,xtim
xtim.cache_dir=str(H/'.xtim_cache')
stem=Path(sys.argv[1]);procs=int(sys.argv[2]);txt=Path(str(stem)+'.qasm').read_text();d=json.loads(Path(str(stem)+'.json').read_text());out=dict(sha256=hashlib.sha256(txt.encode()).hexdigest(),metadata=d)
def save():Path(str(stem)+'.score.json').write_text(json.dumps(out,indent=2)+'\n')
r=tprep.check(txt,d['data_qubits'],shots=10**6,seed=0);Path(str(stem)+'.check.log').write_text(str(r)+'\n');out.update(judge_passed=r.passed,correct_ok=r.correct_ok,acceptance_1e6=r.acceptance);save();print(r,flush=True)
if not r.correct_ok:sys.exit(0)
p=subprocess.run([sys.executable,str(H.parent/'EVAL/exact2.py'),str(stem)+'.qasm','--third','--procs',str(procs),'--top','0'],capture_output=True,text=True)
Path(str(stem)+'.exact.log').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)
if p.returncode:raise RuntimeError(p.stderr)
for k,pat in [('c1',r'c1 p = ([\deE+.\-]+)'),('second',r'1-F \(2nd order\) = ([\deE+.\-]+)'),('total',r'1-F \(to 3rd order\) = ([\deE+.\-]+)'),('exp_A1',r'exp\(-A1\) = ([\deE+.\-]+)')]:
 m=re.search(pat,p.stdout)
 if m:out[k]=float(m.group(1))
if 'total' in out:out['third']=out['total']-out['second']
save()
if abs(out.get('c1',1))>=1e-12 or out.get('total',1)<=8.41984e-5*1.03:
 out['mc']=[]
 for seed in (0,1000,2000):
  r=fast_check.check(txt,d['data_qubits'],shots=10**8,seed=seed,procs=procs);out['mc'].append(dict(seed=seed,score=r.score,acceptance=r.acceptance,sem=r.sem,passed=r.passed));save();print('MC',out['mc'][-1],flush=True)
 out['mean']=sum(x['score'] for x in out['mc'])/3;save()
