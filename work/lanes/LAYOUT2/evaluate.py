import sys,os,json,re,subprocess
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
HERE=Path(__file__).resolve().parent;os.chdir(HERE)
sys.path.insert(0,str(HERE.parents[1]))
import tprep,fast_check,xtim
xtim.cache_dir=str(HERE/'.xtim_cache')
stem=sys.argv[1];procs=int(sys.argv[2]) if len(sys.argv)>2 else 2
text=Path(stem+'.qasm').read_text();d=json.loads(Path(stem+'.json').read_text())
rep=tprep.check(text,d['data_qubits'],shots=10**6,seed=0)
Path(stem+'_check.log').write_text(str(rep)+'\n')
print(rep,flush=True)
out=dict(cx=rep.n_2q,R=d.get('R'),passed=rep.passed,format_errors=rep.format_errors,class_error=rep.class_error,correctness_errors=rep.correctness_errors,check_score=rep.score,acceptance=rep.acceptance)
if rep.correct_ok:
 cmd=[sys.executable,str(HERE.parent/'EVAL/exact2.py'),stem+'.qasm','--third','--procs',str(procs),'--top','0']
 r=subprocess.run(cmd,text=True,capture_output=True)
 Path(stem+'_exact.log').write_text(r.stdout+r.stderr)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 print(r.stdout,flush=True)
 for key,pat in [('first',r'c1 p = ([\deE+.\-]+)'),('second',r'1-F \(2nd order\) = ([\deE+.\-]+)'),('third',r'1-F \(to 3rd order\) = ([\deE+.\-]+)'),('exp_A1',r'exp\(-A1\) = ([\deE+.\-]+)')]:
  match=re.search(pat,r.stdout)
  if match:out[key]=float(match.group(1))
 Path(stem+'_metrics.json').write_text(json.dumps(out,indent=2)+'\n')
 if out.get('third',1)<1.019e-4 and out.get('first',1)<1e-12:
  out['mc']=[]
  for s in (0,1000,2000):
   r=fast_check.check(text,d['data_qubits'],shots=10**8,seed=s,procs=procs)
   out['mc'].append(dict(seed=s,score=r.score,sem=r.sem,acceptance=r.acceptance,passed=r.passed));print('MC',out['mc'][-1],flush=True)
   Path(stem+'_metrics.json').write_text(json.dumps(out,indent=2)+'\n')
else:Path(stem+'_metrics.json').write_text(json.dumps(out,indent=2)+'\n')
