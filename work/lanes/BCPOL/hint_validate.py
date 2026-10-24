"""Check instance-local target/signature hints, including omitted C helpers."""
import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent
from synth import *
import json,copy
base=json.loads((H/'inputs/base.prep.json').read_text());cases=[]
for value in (0,4,6):cases.append(dict(copy.deepcopy(base),kind='c6',value=value,helper_x=True))
for tag in ['rank4_3_00731','rank3_0_00699']:
 cases.append(json.loads((H/'finalists'/f'{tag}.json').read_text())['prep'])
rows=[];models=[]
for i,d in enumerate(cases):
 m=Model(len(d['ops']),sum(map(len,d['ops'])),1800+i,d['kind'],d['value'],helper_x=d.get('helper_x',False),extra_check=d.get('extra_check',False),endpoint_rank=d.get('endpoint_rank'));models.append(m)
 for t,ss in enumerate(m.sel):
  active={tuple(e) for e in d['ops'][t]}
  for e,z in ss.items():m.add([z if e in active else -z]);m.cut((t+1,e))
 for t in range(m.D+1):
  for q in m.cells:m.cut((t,(q,)))
 m.warm(d);assert m.s.solve();v=verify(m.candidate());assert v['stim_target_pass'] and v['policy_pass'];rows.append(dict(kind=d['kind'],value=d['value'],verification=v))
# Re-warm the first model after constructing different targets: no globals leak.
models[0].warm(cases[0]);assert models[0].s.solve();assert verify(models[0].candidate())['policy_pass']
(H/'hint.validation.json').write_text(json.dumps(dict(models=rows,interleaved_model_pass=True),indent=2));print('HINTS_VALIDATED')
