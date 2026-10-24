import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent
from build import build
from synth import verify,B,C,trace
from cache import setup,compile_cache,contract,evaluate
import json,numpy as np,time
base=json.loads((H/'inputs/base.prep.json').read_text());base.update(kind='policy',value=9)
text,md=build(base,dict(timing='project'));init=md['init_times'];stem=H/'inputs/cache_control';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2))
compile_cache(stem,H/'boundary.cache.npz');z=np.load(H/'boundary.cache.npz',allow_pickle=True);rows=[]
for policy in ['alap','random','project']:
 for seed in range(3):
  opt=dict(timing=policy,timing_seed=seed,fixed_init=init);text,md=build(base,opt);stem=H/'inputs/cache_test';stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));ev,b,ks,prep,ext,hh=setup(stem)
  row=dict(policy=policy,seed=seed,compatible=hh==str(z['ext_hash']))
  if row['compatible']:
   cached=contract(ev,prep,z['response'],z['n3']);full=evaluate(ev);delta=cached['total']-full['total'];assert abs(delta)<1e-14
   row.update(cache=cached,full=full,delta=delta)
  rows.append(row);print(json.dumps(row),flush=True)
(H/'cache.validation.json').write_text(json.dumps(rows,indent=2))
