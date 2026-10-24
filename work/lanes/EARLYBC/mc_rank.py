import os,sys,json
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn');sys.path.insert(0,str(ROOT/'work'));import fast_check,tprep
procs=int(sys.argv[1])
for name in sys.argv[2:]:
 stem=ROOT/'work/lanes/EARLYBC'/name;text=stem.with_suffix('.qasm').read_text();data=json.loads(stem.with_suffix('.json').read_text())['data_qubits'];out=[]
 c=tprep.check(text,data,shots=10**6,seed=0);print(name,'check',c,flush=True);assert c.passed
 for seed in (0,1000,2000):
  r=fast_check.check(text,data,shots=10**8,seed=seed,procs=procs);out.append(dict(seed=seed,score=r.score,acceptance=r.acceptance,sem=r.sem,passed=r.passed));stem.with_suffix('.mc.json').write_text(json.dumps(dict(seeds=out,mean=sum(x['score'] for x in out)/len(out)),indent=2));print(name,out[-1],flush=True)
 print(name,'MEAN',sum(x['score'] for x in out)/3,flush=True)
