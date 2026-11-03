import os,sys,json,hashlib
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import stim
R=Path.cwd();H=R/'work/lanes/SOTA_RESOURCE_20261028';sys.path.insert(0,str(R/'work/lanes/END2_20261027'));sys.path.insert(0,str(R/'work/lanes/EXPAND2_20261027'))
from partial_contract import make_partial_contract
from joint_resource_beam import nullspace
p=H/'sol'/f'{sys.argv[1]}.json';s=json.loads(p.read_text());assert s['status'] in ('FEASIBLE','OPTIMAL')
c=make_partial_contract(s['roles'],85,True);cells=s['cells'];piv={int(k):v for k,v in s['pivots'].items()};layers=s['ops'];T=s['T0'];used=set();operations=[]
for q in cells:
 times=[T+i for i,l in enumerate(layers) if any(q in e for e in l)]
 if not times:continue
 operations.append(dict(time=min(times)-1,kind='RX' if piv[q] else 'R',qs=[q]));used.add(q)
for t,l in enumerate(layers):
 for a,b in l:
  assert abs(a//6-b//6)+abs(a%6-b%6)==1
  operations.append(dict(time=T+t,kind='CX',qs=[a,b]))
for x in s['late_initializations']:operations.append(dict(time=x['time'],kind='RX',qs=[x['qubit']]));used.add(x['qubit'])
# Helper flags measure after the last resource gate on their respective cell.
for q in s['helpers']:
 times=[x['time'] for x in operations if q in x['qs']]
 if times:operations.append(dict(time=max(times)+1,kind='M',qs=[q],zero_flag=True))
seen=set()
for o in operations:
 for q in o['qs']:
  key=(o['time'],q);assert key not in seen,key;seen.add(key)
# Check final premeasurement resource state on all 22 wires.
sim=stim.TableauSimulator();sim.set_num_qubits(36)
for q,v in piv.items():
 if v:sim.h(q)
for layer in layers:
 for a,b in layer:sim.cx(a,b)
for x in s['late_initializations']:sim.reset(x['qubit']);sim.h(x['qubit'])
rows=c.FULL_ROWS[4:]
checks=[]
for support in rows:
 st=stim.PauliString(36)
 for q in support:st[q]='X'
 checks.append(sim.peek_observable_expectation(st))
rmasks=[sum(1<<cells.index(q) for q in r) for r in rows]
for mask in nullspace(rmasks,len(cells)):
 st=stim.PauliString(36)
 for i,q in enumerate(cells):
  if mask>>i&1:st[q]='Z'
 checks.append(sim.peek_observable_expectation(st))
assert len(checks)==len(cells) and set(checks)=={1},checks
out=dict(roles=s['roles'],square_mask=85,operations=operations,cx=s['cx'],depth=s['depth'],helpers=s['helpers'],source_solution=str(p),initialization_contract='All used cells available for independent reset at listed times.',checked_stabilizers=len(checks),validation='All +1 final target CSS stabilizers; native CX adjacency and per-cell timing checked.',scope='Standalone resource only. No source, terminal, noise or acceptance claim.')
(H/f'{sys.argv[1]}_module.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'cx':s['cx'],'depth':s['depth'],'checked':len(checks),'module':str(H/f'{sys.argv[1]}_module.json')}))
