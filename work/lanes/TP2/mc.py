import os,sys,json,hashlib
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;sys.path.insert(0,str(H.parents[1]));os.chdir(H)
import fast_check,xtim,tprep
xtim.cache_dir=str(H/'.xtim_cache')
stem=H/sys.argv[1];procs=int(sys.argv[2]);txt=stem.with_suffix('.qasm').read_text();data=json.loads(stem.with_suffix('.json').read_text())['data_qubits'];out=dict(sha256=hashlib.sha256(txt.encode()).hexdigest(),shots=10**8,mc=[])
check=tprep.check(txt,data,shots=10**6,seed=0);out['judge_1e6']=dict(passed=check.passed,correct_ok=check.correct_ok,acceptance=check.acceptance);print(check,flush=True)
assert check.correct_ok
for seed in (0,1000,2000):
 print('capacity',os.cpu_count(),Path('/proc/loadavg').read_text().strip(),flush=True)
 r=fast_check.check(txt,data,shots=10**8,seed=seed,procs=procs)
 out['mc'].append(dict(seed=seed,score=r.score,sem=r.sem,acceptance=r.acceptance,passed=r.passed));print(out['mc'][-1],flush=True)
 out['mean']=sum(x['score'] for x in out['mc'])/len(out['mc']);Path(str(stem)+'.mc.json').write_text(json.dumps(out,indent=2)+'\n')
