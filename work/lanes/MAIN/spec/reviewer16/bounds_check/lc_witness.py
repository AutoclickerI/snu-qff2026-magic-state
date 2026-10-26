"""Construct and statevector-verify a noisy-cost-not-priced Clifford preparation witness.

Every LC is implemented physically as SX(center) and Sdg(neighbors), then Z measurement.
No conditional physical gate is used. Outcome-dependent Paulis are tracked symbolically.
The target is Steane |+_L>, suitable for the C block of the square contract, where both
Pauli axes can be folded into later detector parities. This is NOT a fault-safe circuit proof.
"""
from lc_probe import graph,lc
from collections import deque,Counter
from itertools import permutations,product
from pathlib import Path
import json,numpy as np

base=graph(7,[(0,2),(0,4),(0,6),(1,2),(1,5),(1,6),(3,4),(3,5),(3,6)])
parent={base:None};todo=deque([base])
while todo:
 g=todo.popleft()
 for v in range(7):
  h=lc(g,v)
  if h not in parent:parent[h]=(g,v);todo.append(h)
hit=json.loads(Path('bounds_check/lc_hit.json').read_text())
kept=[i for i in range(11) if i not in hit['removed']]
current=tuple(hit['graph_after'])
for perm in permutations(range(7)):
 align=tuple(sum(((current[perm[i]]>>perm[j])&1)<<j for j in range(7)) for i in range(7))
 if align in parent:break
path=[];s=align
while parent[s] is not None:
 prev,v=parent[s];path.append(v);s=prev
physical_output=[kept[perm[i]] for i in range(7)]

neighbors={i:set() for i in range(11)}
for u,v in hit['edges']:neighbors[u].add(v);neighbors[v].add(u)
ops=[];xf={i:0 for i in range(11)};zf=dict(xf);measurement_order=[]
def complement(v):
 ns=sorted(neighbors[v]);ops.append(['sx',v]);xf[v]^=zf[v]
 for u in ns:ops.append(['sdg',u]);zf[u]^=xf[u]
 for ii,u in enumerate(ns):
  for w in ns[ii+1:]:
   if w in neighbors[u]:neighbors[u].remove(w);neighbors[w].remove(u)
   else:neighbors[u].add(w);neighbors[w].add(u)
def mz(v):
 r=len(measurement_order);measurement_order.append(v);ops.append(['m',v,r])
 actual_outcome=(1<<r)^xf[v]
 for u in neighbors[v]:zf[u]^=actual_outcome;neighbors[u].remove(v)
 del neighbors[v];del xf[v];del zf[v]

for v,basis in reversed(tuple(zip(hit['removed'],hit['bases']))):
 if basis=='X':
  u=min(neighbors[v]);complement(u);complement(v);complement(u)
 elif basis=='Y':complement(v)
 mz(v)
for label in path:complement(physical_output[label])
# Graph -> Steane |+L>: H on systematic generator pivots 0,1,3.
for label in [0,1,3]:
 v=physical_output[label];ops.append(['h',v]);xf[v],zf[v]=zf[v],xf[v]

I=np.eye(2,dtype=complex); X=np.array([[0,1],[1,0]],complex)
H=np.array([[1,1],[1,-1]],complex)/np.sqrt(2)
SX=(I-1j*X)/np.sqrt(2); SDG=np.diag([1,-1j]); Z=np.diag([1,-1])
def one(st,u,v):
 out=st.copy()
 for i in range(len(st)):
  if not(i>>v&1):
   j=i|(1<<v);out[i]=u[0,0]*st[i]+u[0,1]*st[j];out[j]=u[1,0]*st[i]+u[1,1]*st[j]
 return out
initial=np.ones(1<<11,complex)/np.sqrt(1<<11)
for u,v in hit['edges']:
 for i in range(len(initial)):
  if (i>>u&1) and (i>>v&1):initial[i]*=-1
# |+L> is uniform over Hamming code (span X stabilizers and all-ones).
code={0}
for r in [0b1010101,0b1100110,0b1111000,0b1111111]:code|={x^r for x in tuple(code)}
target=np.zeros(128,complex)
for w in code:target[w]=.25
records=[];worst=0
for bits in product([0,1],repeat=4):
 st=initial.copy();prob=1
 for op in ops:
  if op[0]=='m':
   _,v,r=op;mask=np.array([((i>>v)&1)==bits[r] for i in range(len(st))]);st*=mask
   p=float(np.vdot(st,st).real);prob*=p;st/=np.sqrt(p)
  else:st=one(st,{'sx':SX,'sdg':SDG,'h':H}[op[0]],op[1])
 # Numerical verification applies the recorded Pauli virtually, not physically.
 mask=sum(b<<j for j,b in enumerate(bits))
 for v in physical_output:
  if (xf[v]&mask).bit_count()%2:st=one(st,X,v)
  if (zf[v]&mask).bit_count()%2:st=one(st,Z,v)
 out=np.zeros(128,complex)
 fixed=sum(bits[r]<<v for r,v in enumerate(measurement_order))
 for w in range(128):
  i=fixed|sum(((w>>j)&1)<<v for j,v in enumerate(physical_output));out[w]=st[i]
 fid=float(abs(np.vdot(target,out))**2);worst=max(worst,abs(1-fid))
 records.append({'bits':bits,'probability':prob,'fidelity_after_virtual_frame':fid})
result={'coords':hit['coords'],'edges':hit['edges'],'output_labels_to_vertices':physical_output,'output_labels_to_grid6':[6*hit['coords'][i][0]+hit['coords'][i][1] for i in physical_output],
 'measurement_order_vertices':measurement_order,'measurement_order_grid6':[6*hit['coords'][i][0]+hit['coords'][i][1] for i in measurement_order],
 'final_graph_to_base_lc_labels':path,'ops_after_graph':ops,'op_counts_after_graph':dict(Counter(x[0] for x in ops)),
 'pauli_frame_x_masks':[xf[v] for v in physical_output],'pauli_frame_z_masks':[zf[v] for v in physical_output],
 'branches':records,'worst_fidelity_error':worst,
 'warning':'Ideal constructive witness only. Includes explicit physical local Clifford units; no native noise or fault safety claim. Used as square C: full Pauli byproducts must be XORed into B/C/A detector readouts.'}

# All LC gates are local and no gate acts on a measured helper afterwards.
# Commute local gates to a single local Clifford per surviving/measured wire.
S=np.diag([1,1j]);Y=np.array([[0,-1j],[1j,0]])
gates={'h':H,'s':S,'sdg':SDG,'sx':SX,'sxdg':SX.conj().T,'x':X,'y':Y,'z':Z}
def key(u):
 a=next(x for x in u.flat if abs(x)>1e-8);u=u/(a/abs(a))
 return tuple(np.round(u.real,10).flat)+tuple(np.round(u.imag,10).flat)
short={key(I):[]};unit={key(I):I};todo=deque([key(I)])
while todo:
 k=todo.popleft()
 for name,u in gates.items():
  new=u@unit[k];kk=key(new)
  if kk not in short:short[kk]=short[k]+[name];unit[kk]=new;todo.append(kk)
assert len(short)==24
local={v:I.copy() for v in range(11)}
for op in ops:
 if op[0]!='m':local[op[1]]=gates[op[0]]@local[op[1]]
black={v for v,(r,c) in enumerate(hit['coords']) if (r+c)%2}
for v in black:local[v]=local[v]@H
flips=0;measures={}
for r,v in enumerate(measurement_order):
 obs=local[v].conj().T@Z@local[v]
 matches=[(name,sgn) for name,p in [('X',X),('Y',Y),('Z',Z)] for sgn in [1,-1] if np.max(abs(obs-sgn*p))<1e-9]
 assert len(matches)==1
 name,sgn=matches[0];measures[v]=name
 if sgn<0:flips|=1<<r
outlocals={}
for v in physical_output:
 u=local[v]
 if (xf[v]&flips).bit_count()%2:u=X@u
 if (zf[v]&flips).bit_count()%2:u=Z@u
 outlocals[v]=short[key(u)]
result['compressed']={'graph_cx_edges':[(v,u) if u in black else (u,v) for u,v in hit['edges']],
 'init_X_vertices':[v for v in range(11) if v not in black],'init_Z_vertices':sorted(black),
 'output_local_gates':outlocals,'measure_bases_vertices':measures,'virtual_original_record_flips_mask':flips,
 'pauli_frame_x_masks':[xf[v] for v in physical_output],'pauli_frame_z_masks':[zf[v] for v in physical_output],
 'single_qubit_output_gate_count':sum(len(v) for v in outlocals.values()),'Y_measure_extra_Sdg_count':sum(b=='Y' for b in measures.values())}
st0=np.zeros(1<<11,complex);st0[0]=1
for v in range(11):
 if v not in black:st0=one(st0,H,v)
for c,t in result['compressed']['graph_cx_edges']:
 out=st0.copy()
 for i in range(len(st0)):out[i ^ ((1<<t) if (i>>c&1) else 0)]=st0[i]
 st0=out
for v,seq in outlocals.items():
 for g in seq:st0=one(st0,gates[g],v)
for v,b in measures.items():
 if b=='Y':st0=one(st0,SDG,v)
 if b in ['X','Y']:st0=one(st0,H,v)
compressed_worst=0;compressed_records=[]
for bits in product([0,1],repeat=4):
 st=st0.copy();prob=1
 for r,v in enumerate(measurement_order):
  st*=np.array([((i>>v)&1)==bits[r] for i in range(len(st))]);p=float(np.vdot(st,st).real);prob*=p;st/=np.sqrt(p)
 mask=sum(b<<j for j,b in enumerate(bits))
 for v in physical_output:
  if (xf[v]&mask).bit_count()%2:st=one(st,X,v)
  if (zf[v]&mask).bit_count()%2:st=one(st,Z,v)
 out=np.zeros(128,complex);fixed=sum(bits[r]<<v for r,v in enumerate(measurement_order))
 for w in range(128):out[w]=st[fixed|sum(((w>>j)&1)<<v for j,v in enumerate(physical_output))]
 fid=float(abs(np.vdot(target,out))**2);compressed_worst=max(compressed_worst,abs(1-fid));compressed_records.append({'bits':bits,'probability':prob,'fidelity':fid})
result['compressed']['worst_fidelity_error']=compressed_worst
result['compressed']['branches']=compressed_records
assert compressed_worst<1e-12
Path('bounds_check/lc_witness.json').write_text(json.dumps(result,indent=2))
qmap={i:6*r+c for i,(r,c) in enumerate(hit['coords'])}
used=sorted(qmap.values());bar='barrier '+','.join(f'q[{q}]' for q in used)+';'
qasm=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];','creg c[4];',
 '// Ideal C-resource witness only: not a full T-state submission; all four records retained.',
 '// Physical Pauli byproducts listed in lc_witness.json must be folded into square detectors.']
for v in range(11):
 qasm.append(f'reset q[{qmap[v]}];')
 if v not in black:qasm.append(f'h q[{qmap[v]}];')
for color in range(4):
 qasm.append(bar)
 for c,t in result['compressed']['graph_cx_edges']:
  r1,c1=hit['coords'][c];r2,c2=hit['coords'][t]
  edgecolor=min(c1,c2)%2 if r1==r2 else 2+min(r1,r2)%2
  if edgecolor==color:qasm.append(f'cx q[{qmap[c]}],q[{qmap[t]}];')
qasm.append(bar)
for v,seq in outlocals.items():
 if seq:qasm.append(f'{seq[0]} q[{qmap[v]}];')
for v,b in measures.items():
 if b=='Y':qasm.append(f'sdg q[{qmap[v]}];')
qasm.append(bar)
for v,seq in outlocals.items():
 if len(seq)>1:qasm.append(f'{seq[1]} q[{qmap[v]}];')
for r,v in enumerate(measurement_order):
 if measures[v] in ['X','Y']:qasm.append(f'h q[{qmap[v]}];')
 qasm.append(f'measure q[{qmap[v]}] -> c[{r}];')
Path('bounds_check/lc_c_resource.qasm').write_text('\n'.join(qasm)+'\n')
print(json.dumps({'worst_fidelity_error':worst,'compressed':{k:v for k,v in result['compressed'].items() if k!='branches'}},indent=2))
assert worst<1e-12
