"""Export measured-helper native resource. Full source contract must be derived separately."""
import os,sys,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import stim
R=Path.cwd();H=R/'work/lanes/SOTA_RESOURCE_20261028';sys.path.insert(0,str(R/'work/lanes/END2_20261027'));sys.path.insert(0,str(R/'work/lanes/EXPAND2_20261027'))
from partial_contract import make_partial_contract
from joint_resource_beam import nullspace
p=H/'sol'/f'{sys.argv[1]}.json';s=json.loads(p.read_text());assert s['status'] in ('FEASIBLE','OPTIMAL')
c=make_partial_contract(s['roles'],45,True);cells=s['cells'];outcells=c.B+c.C;piv={int(k):v for k,v in s['pivots'].items()};layers=s['ops'];T=s['T0'];operations=[]
for q in cells:
 times=[T+i for i,l in enumerate(layers) if any(q in e for e in l)]
 if not times:continue
 operations.append(dict(time=min(times)-1,kind='RX' if piv[q] else 'R',qs=[q]))
for t,l in enumerate(layers):
 for a,b in l:
  assert abs(a//6-b//6)+abs(a%6-b%6)==1
  operations.append(dict(time=T+t,kind='CX',qs=[a,b]))
for x in s['late_initializations']:operations.append(dict(time=x['time'],kind='RX',qs=[x['qubit']]))
helpers_used=[]
for q in s['helpers']:
 times=[x['time'] for x in operations if q in x['qs']]
 if times:operations.append(dict(time=max(times)+1,kind='MX',qs=[q]));helpers_used.append(q)
seen=set()
for o in operations:
 for q in o['qs']:
  key=(o['time'],q);assert key not in seen,key;seen.add(key)
# After MX helper reads, target X stabilizers may acquire outcome-dependent
# signs (Z frame); the signs are tracked by full record-contract completion.
sim=stim.TableauSimulator();sim.set_num_qubits(36)
for q,v in piv.items():
 if v:sim.h(q)
for layer in layers:
 for a,b in layer:sim.cx(a,b)
for x in s['late_initializations']:sim.reset(x['qubit']);sim.h(x['qubit'])
measured={q:sim.measure_x(q) for q in helpers_used}
rows=c.FULL_ROWS[4:];checks=[]
for support in rows:
 st=stim.PauliString(36)
 for q in support:st[q]='X'
 checks.append(sim.peek_observable_expectation(st))
rmasks=[sum(1<<outcells.index(q) for q in r) for r in rows]
zchecks=[]
for mask in nullspace(rmasks,len(outcells)):
 st=stim.PauliString(36)
 for i,q in enumerate(outcells):
  if mask>>i&1:st[q]='Z'
 zchecks.append(sim.peek_observable_expectation(st))
assert len(checks)+len(zchecks)==len(outcells) and all(abs(v)==1 for v in checks) and set(zchecks)=={1},(checks,zchecks)
out=dict(roles=s['roles'],square_mask=45,operations=operations,cx=s['cx'],depth=s['depth'],helpers=helpers_used,source_solution=str(p),measured_helpers=True,checked_output_stabilizers=len(checks)+len(zchecks),example_X_stabilizer_signs=checks,example_helper_outcomes=measured,validation='Native CX adjacency, no per-cell collisions, and full conditional CSS state checked; X signs depend on MX helper outcomes.',scope='Standalone resource only. Record outcomes must be retained in a complete source/terminal contract; no noisy score claim.')
name=H/f'{sys.argv[1]}_module.json';name.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'cx':s['cx'],'depth':s['depth'],'helpers':helpers_used,'module':str(name)},flush=True))
