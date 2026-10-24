import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
H=Path(__file__).resolve().parent
from synth import *
import json
rows=[]
for rank,values in [(6,[0]),(5,range(1,8)),(4,range(1,8)),(3,[0])]:
 for value in values:
  gs=generators('endpoint',value,rank);assert len(span(gs))==2**rank
  flags=extra_cells(value,rank) if rank<6 else []
  assert all(not(g>>q&1) for q in flags for g in gs[3:])
  cols=[sum(1<<i for i in r) for r in ROWS]+[127]+[1<<C.index(q) for q in flags]
  assert len(span(cols))==2**(10-rank)
  rows.append(dict(rank=rank,value=value,flag_cells=flags,generator_count=len(gs)))
# Explicit six-CX, two-layer C6 encoder on a 2x3 patch.
placement={0:0,2:1,1:2,4:6,3:7,5:8};layers=[[(0,2),(1,5),(3,4)],[(0,4),(1,2),(3,5)]];c=stim.Circuit()
for q in placement.values():c.append('R',[q])
for q in (0,1,3):c.append('H',[placement[q]])
for lay in layers:
 seen=set()
 for a,b in lay:
  u,v=placement[a],placement[b];assert v in nb(u) and not ({u,v}&seen);seen|={u,v};c.append('CX',[u,v])
sim=stim.TableauSimulator();sim.do(c)
for kind,sets in [('X',[[0,2,4],[1,2,5],[3,4,5]]),('Z',[[0,1,2],[0,3,4],[1,3,5]])]:
 for ss in sets:
  p=stim.PauliString(9)
  for q in ss:p[placement[q]]=kind
  assert sim.peek_observable_expectation(p)==1
(H/'contracts.full_validation.json').write_text(json.dumps(dict(endpoints=rows,C6_encoder=dict(placement=placement,layers=layers,cx=6,depth=2,stim_pass=True)),indent=2));print('ALL_16_ENDPOINTS_AND_LOCAL_C6_VALIDATED')
