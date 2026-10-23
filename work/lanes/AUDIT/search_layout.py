import sys,random
sys.path.insert(0,'.')
from qiskit import QuantumCircuit,transpile
from qiskit.transpiler import CouplingMap
N=36; SUP=[{0,2,4,6},{1,2,5,6},{3,4,5,6}]; req=[i for s in SUP for i in sorted(s)]
def match(data):
 al=[]
 for r in req:
  a=data[r]; al.append([q for q in range(N) if q not in data and abs(q//6-a//6)+abs(q%6-a%6)==1])
 mr=[-1]*N; rr=[-1]*len(req)
 def dfs(r,seen):
  for q in al[r]:
   if seen>>q&1:continue
   seen|=1<<q
   if mr[q]<0 or dfs(mr[q],seen):mr[q]=r;rr[r]=q;return True
  return False
 for r in sorted(range(len(req)),key=lambda r:len(al[r])):
  if not dfs(r,0):return None
 return rr
qc=QuantumCircuit(7)
qc.h(0);qc.t(0);qc.h(1);qc.cx(0,4);qc.cx(4,0);qc.cx(0,4);qc.cx(1,0);qc.h(2);qc.cx(1,5);qc.cx(5,1);qc.cx(1,5);qc.cx(2,1);qc.cx(4,5);qc.cx(5,2);qc.cx(2,4);qc.h(3);qc.cx(5,6);qc.cx(4,3);qc.cx(3,5);qc.cx(5,4);qc.cx(4,6);qc.cx(6,3);qc.cx(3,6);qc.cx(6,3)
cm=CouplingMap.from_grid(6,6)
best=[];rng=random.Random(0)
for t in range(100):
 init=rng.sample(range(36),7)
 try:r=transpile(qc,coupling_map=cm,basis_gates=['h','t','cx'],optimization_level=3,seed_transpiler=t,initial_layout=init)
 except Exception:continue
 d=list(r.layout.final_index_layout()[:7]); m=match(d)
 if m:
  print('FOUND',t,'init',init,d,'2q',r.count_ops().get('cx',0),'m',m,flush=True);break
 best.append((r.count_ops().get('cx',0),d))
else: print('none best',sorted(best)[:10])
