import sys
sys.path.insert(0,'/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem')
from qiskit import QuantumCircuit,transpile
from qiskit.transpiler import CouplingMap
from pathlib import Path
import tprep
# logical target preparation from problem.md
qc=QuantumCircuit(7)
qc.h(0);qc.t(0);qc.h(1);qc.cx(0,4);qc.cx(4,0);qc.cx(0,4);qc.cx(1,0);qc.h(2);qc.cx(1,5);qc.cx(5,1);qc.cx(1,5);qc.cx(2,1);qc.cx(4,5);qc.cx(5,2);qc.cx(2,4);qc.h(3);qc.cx(5,6);qc.cx(4,3);qc.cx(3,5);qc.cx(5,4);qc.cx(4,6);qc.cx(6,3);qc.cx(3,6);qc.cx(6,3)
cm=CouplingMap.from_grid(6,6)
# deterministic layout search result
r=transpile(qc,coupling_map=cm,basis_gates=['h','t','cx'],optimization_level=3,seed_transpiler=32,initial_layout=[26,2,10,28,4,8,22])
# verify actual data mapping
D=list(r.layout.final_index_layout()[:7])
# matching for requests S1,S2,S3
SUP=[{0,2,4,6},{1,2,5,6},{3,4,5,6}]
req=[i for s in SUP for i in sorted(s)]
def matching(data):
 al=[]
 for i in req:
  a=data[i];al.append([q for q in range(36) if q not in data and abs(q//6-a//6)+abs(q%6-a%6)==1])
 mr=[-1]*36;rr=[-1]*12
 def dfs(k,seen):
  for q in al[k]:
   if seen>>q&1:continue
   seen|=1<<q
   if mr[q]<0 or dfs(mr[q],seen):mr[q]=k;rr[k]=q;return 1
  return 0
 for k in sorted(range(12),key=lambda k:len(al[k])):
  if not dfs(k,0):raise RuntimeError('no match')
 return rr
A=matching(D)
print('DATA',D,'ANC',A,'ops',r.count_ops())
text=tprep.submission_text(r)
lines=text.splitlines()
qi=next(i for i,x in enumerate(lines) if x.startswith('qreg'))
lines.insert(qi+1,'creg c[24];')
# add checks, ancilla reuse sequentially; detector each check
idx=0
for basis in ('X','Z'):
 for si,s in enumerate(SUP):
  for j,i in enumerate(sorted(s)):
   a=A[sum(len(x) for x in SUP[:si])+j]
   lines.append(f'reset q[{a}];')
   if basis=='X':
    lines.append(f'h q[{a}];')
    lines.append(f'cx q[{a}],q[{D[i]}];')
    lines.append(f'h q[{a}];')
   else:
    lines.append(f'cx q[{D[i]}],q[{a}];')
   lines.append(f'measure q[{a}] -> c[{idx}];')
   idx+=1
  cs=' '.join(f'c[{idx-4+j}]' for j in range(4))
  lines.append('// DETECTOR '+cs)
Path('/home/jihoon/competitions/quantumn/work/lanes/AUDIT/checks.qasm').write_text('\n'.join(lines)+'\n')
print('wrote',len(lines))
