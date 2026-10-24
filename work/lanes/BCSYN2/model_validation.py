import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json
from pathlib import Path
from synth import Model,verify
H=Path(__file__).resolve().parent;groups=json.loads((H/'lns_unique.json').read_text());paths=[H/'inputs/clean82.prep.json']+[H.parents[2]/groups[i][0] for i in (0,1,10,100,300,1000,1500,2134)]
rows=[]
for f in paths:
 d=json.loads(f.read_text());m=Model(14,82,seed=13);m.warm(d)
 for t in range(15):
  for q in m.cells:m.cut((t,(q,)))
 for t,ss in enumerate(m.sel):
  for e in ss:m.cut((t+1,e))
 for t,ss in enumerate(m.sel):
  act={tuple(e) for e in d['ops'][t]}
  for e,z in ss.items():m.add([z if e in act else -z])
 ok=m.s.solve();v=verify(d);assert ok and v['stim_target_pass'] and v['clean_pass'];rows.append(dict(file=str(f),solver='SAT',verification=v))
 d2=m.candidate();assert set(d2['pivots'])==set(d['pivots'])
 m.s.delete()
(H/'model_validation.json').write_text(json.dumps(rows,indent=2));print(len(rows),'fixed networks match independent Stim and BC2 predicate')
# Demonstrate the helper-X relaxation on a known state: one copy onto q32,
# then postselection of its X outcome yields the original B+C target.
d=json.loads((H/'inputs/clean82.prep.json').read_text());d['ops'].append([[26,32]]);d['cells']=[6,26,13,11,4,23,27,12,25,19,17,5,29,28,32];d['helper_x']=True
v=verify(d);assert v['stim_target_pass'] and v['clean_pass'];d['verification']=v;(H/'runs/helper_x_known.prep.json').write_text(json.dumps(d,indent=2));print(v)
