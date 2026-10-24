import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,math,time
H=Path(__file__).resolve().parent
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
from synth import *
from search import score
base=json.loads((H/'inputs/base.prep.json').read_text());rows=[]
for kind,value in [('policy',v) for v in range(9,16)]+[('endpoint',0)]:
 d=json.loads(json.dumps(base));d.update(kind=kind,value=value)
 if kind=='endpoint':d['ops'].append([list(e) for e in zip(B,C)])
 v=verify(d);assert v['stim_target_pass'] and v['policy_pass'],v
 m=Model(len(d['ops']),sum(map(len,d['ops'])),17,kind,value)
 for t,ss in enumerate(m.sel):
  act={tuple(e) for e in d['ops'][t]}
  for e,z in ss.items():m.add([z if e in act else -z]);m.cut((t+1,e))
 for t in range(m.D+1):
  for q in m.cells:m.cut((t,(q,)))
 assert m.s.solve(),(kind,value)
 vv=verify(m.candidate());assert vv['stim_target_pass'] and vv['policy_pass'],vv
 rows.append(dict(kind=kind,value=value,verification=v,sat=True));m.s.delete()
 if value in (9,0):
  row,text,md=score(d,dict(timing='project'));out=H/'inputs'/f'replay_{kind}';out.with_suffix('.qasm').write_text(text);out.with_suffix('.json').write_text(json.dumps(md,indent=2));rows[-1]['price']=row
  print(json.dumps(rows[-1]),flush=True)
# Exact algebraic endpoint and C6 accepted-sector proof.
S=span([sum(1<<i for i in row) for row in ROWS]);proof=[]
for i in range(7):
 W=S|{s^(1<<i) for s in S};accepted=[x for x in range(128) if (x&~(1<<i)) in {s&~(1<<i) for s in S}]
 assert set(accepted)==W
 assert all(not ft.dangerous(ft.sig({B[j] for j in range(7) if x>>j&1},B)) for x in accepted)
 proof.append(dict(omitted=i,patterns=accepted))
rows.append(dict(c6_sector_proofs=proof,rank5_generators=[generators('endpoint',v) for v in range(1,8)]))
(H/'validation.json').write_text(json.dumps(rows,indent=2));print('VALIDATED',flush=True)
