import os,sys,json,dataclasses,time
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'upstream/snu-qff2026-problem'));sys.path.insert(0,str(HERE/'inputs'))
import fast_check,tprep
p=Path(sys.argv[1]);procs=int(sys.argv[2]);assert os.getloadavg()[0]<os.cpu_count()-procs
text=p.read_text();data=json.loads(p.with_suffix('.json').read_text())['data_qubits'];out=dict(shots=10**8,seeds=[],circuit=str(p))
for seed in [0,1000,2000]:
 t=time.time();r=fast_check.check(text,data,shots=10**8,seed=seed,procs=procs)
 out['seeds'].append(dict(seed=seed,score=r.score,acceptance=r.acceptance,passed=r.passed,sem=r.sem,seconds=time.time()-t));out['mean']=sum(x['score'] for x in out['seeds'])/len(out['seeds']);p.with_suffix('.mc.json').write_text(json.dumps(out,indent=2)+'\n');print(out['seeds'][-1],flush=True)
print('mean',out['mean'],flush=True)
