"""Native schedule, full 1e6 judge, exact2 --third; optionally official three seeds."""
import os,sys,json,re,subprocess,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
HERE=Path(__file__).resolve().parent;ROOT=Path('/home/jihoon/competitions/quantumn');os.chdir(HERE)
sys.path[:0]=[str(ROOT/'work'),str(ROOT/'work/lanes/EVAL')]
import tprep,xtim,fast_check
xtim.cache_dir=str(HERE/'.xtim_cache')
stem=Path(sys.argv[1]);procs=int(sys.argv[2]);mc='--mc' in sys.argv
txt=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text());data=meta['data_qubits']
out=dict(sha256=hashlib.sha256(txt.encode()).hexdigest(),data_qubits=data)
def save():stem.with_suffix('.score.json').write_text(json.dumps(out,indent=1))
r=tprep.check(txt,data,shots=10**6,seed=0);stem.with_suffix('.check.log').write_text(str(r)+'\n');print(r,flush=True)
out.update(judge_passed=r.passed,correct_ok=r.correct_ok,acceptance_1e6=r.acceptance);save()
if not r.correct_ok:sys.exit(0)
cmd=[sys.executable,str(ROOT/'work/lanes/EVAL/exact2.py'),str(stem.with_suffix('.qasm')),'--third','--procs',str(procs),'--top','0']
p=subprocess.run(cmd,capture_output=True,text=True);stem.with_suffix('.exact.log').write_text(p.stdout+p.stderr);print(p.stdout,flush=True)
assert p.returncode==0,p.stderr
for k,pat in [('c1',r'c1 p = ([\deE+.\-]+)'),('second',r'1-F \(2nd order\) = ([\deE+.\-]+)'),('third',r'third order: ([\deE+.\-]+)'),('total',r'1-F \(to 3rd order\) = ([\deE+.\-]+)'),('exp_A1',r'exp\(-A1\) = ([\deE+.\-]+)')]:
 m=re.search(pat,p.stdout)
 if m:out[k]=float(m.group(1))
save()
if mc or abs(out.get('c1',0))>=1e-12:
 out['seeds']=[]
 for seed in [0,1000,2000]:
  r=fast_check.check(txt,data,shots=10**8,seed=seed,procs=procs)
  out['seeds'].append(dict(seed=seed,score=r.score,acceptance=r.acceptance,sem=r.sem,passed=r.passed));save();print(out['seeds'][-1],flush=True)
 out['mean']=sum(x['score'] for x in out['seeds'])/3;save();print('mean',out['mean'],flush=True)
