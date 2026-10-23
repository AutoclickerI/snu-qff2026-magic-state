import sys,heapq
sys.path.insert(0,'/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem')
from qiskit import QuantumCircuit,transpile
from qiskit.transpiler import CouplingMap
from pathlib import Path
import tprep
D=[14,3,8,22,16,21,28]
SUP=[{0,2,4,6},{1,2,5,6},{3,4,5,6}]
# prepare transpiled target exactly as build_checks
qc=QuantumCircuit(7)
qc.h(0);qc.t(0);qc.h(1);qc.cx(0,4);qc.cx(4,0);qc.cx(0,4);qc.cx(1,0);qc.h(2);qc.cx(1,5);qc.cx(5,1);qc.cx(1,5);qc.cx(2,1);qc.cx(4,5);qc.cx(5,2);qc.cx(2,4);qc.h(3);qc.cx(5,6);qc.cx(4,3);qc.cx(3,5);qc.cx(5,4);qc.cx(4,6);qc.cx(6,3);qc.cx(3,6);qc.cx(6,3)
r=transpile(qc,coupling_map=CouplingMap.from_grid(6,6),basis_gates=['h','t','cx'],optimization_level=3,seed_transpiler=32,initial_layout=[26,2,10,28,4,8,22])
assert list(r.layout.final_index_layout()[:7])==D
text=tprep.submission_text(r); lines=text.splitlines(); qi=next(i for i,x in enumerate(lines) if x.startswith('qreg')); lines.insert(qi+1,'creg c[6];')
DATA=set(D); start=0
# paths among non-data cells; ancilla is current location. route to best neighbor of target.
def neigh(q):
 r,c=divmod(q,6)
 for x in (q-1,q+1,q-6,q+6):
  if 0<=x<36 and abs(x//6-r)+abs(x%6-c)==1:yield x
def path(a, goals):
 # choose shortest to any goal
 prev={a:None}; q=[a]
 for x in q:
  if x in goals:
   out=[]
   while x is not None:out.append(x);x=prev[x]
   return out[::-1]
  for y in neigh(x):
   if y in DATA or y in prev:continue
   prev[y]=x;q.append(y)
 raise RuntimeError((a,goals))
def route(a,goal):
 p=path(a,{goal});
 for x,y in zip(p,p[1:]):
  lines.extend([f'cx q[{x}],q[{y}];',f'cx q[{y}],q[{x}];',f'cx q[{x}],q[{y}];'])
 return goal,len(p)-1
# choose nearest allowed neighbor for each target greedily
idx=0; cur=start
for basis in ('X','Z'):
 for s in SUP:
  # reset current location, X prep
  lines.append(f'reset q[{cur}];')
  if basis=='X': lines.append(f'h q[{cur}];')
  for i in sorted(s):
   goals=[x for x in neigh(D[i]) if x not in DATA]
   # choose goal minimizing current distance
   # compute paths lengths
   best=None
   for g in goals:
    try:p=path(cur,{g})
    except RuntimeError:continue
    cand=(len(p),g,p)
    if best is None or cand[:2]<best[:2]:best=cand
   if best is None:raise RuntimeError((basis,s,i,cur,goals))
   _,g,p=best
   for x,y in zip(p,p[1:]): lines.extend([f'cx q[{x}],q[{y}];',f'cx q[{y}],q[{x}];',f'cx q[{x}],q[{y}];'])
   cur=g
   if basis=='X': lines.append(f'cx q[{cur}],q[{D[i]}];')
   else: lines.append(f'cx q[{D[i]}],q[{cur}];')
  if basis=='X': lines.append(f'h q[{cur}];')
  lines.append(f'measure q[{cur}] -> c[{idx}];')
  lines.append(f'// DETECTOR c[{idx}]')
  idx+=1
Path('/home/jihoon/competitions/quantumn/work/lanes/AUDIT/route_checks.qasm').write_text('\n'.join(lines)+'\n')
print('cur',cur,'lines',len(lines),'statements',sum(x.count(';') for x in lines),'2q',sum(x.startswith('cx ') for x in lines))
