"""Placement/schedule screen for the compact Fig.5a candidate."""
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import CHGate
from qiskit.transpiler import CouplingMap
import tprep, json, pathlib, random, sys
sys.path.insert(0,'work/lanes/EVAL')
from exact2 import Eval, run
N=36; data=list(range(7)); a=7; f=8; cm=CouplingMap.from_grid(6,6)
def base():
 qc=QuantumCircuit(N,2)
 qc.h(0);qc.t(0);qc.h(1)
 for x in [(0,4),(4,0),(0,4),(1,0)]:qc.cx(*x)
 qc.h(2)
 for x in [(1,5),(5,1),(1,5),(2,1),(4,5),(5,2),(2,4)]:qc.cx(*x)
 qc.h(3)
 for x in [(5,6),(4,3),(3,5),(5,4),(4,6),(6,3),(3,6),(6,3)]:qc.cx(*x)
 for q in data:qc.h(q)
 for q in data:qc.sdg(q)
 qc.reset(a);qc.reset(f);qc.h(a);qc.cx(a,f)
 for q in reversed(data):qc.append(CHGate(),[a,q])
 qc.cx(a,f);qc.h(a);qc.measure(a,0);qc.measure(f,1)
 for q in data:qc.s(q)
 for q in data:qc.h(q)
 return qc
def compile_one(phys,seed,opt=1):
 tr=transpile(base(),basis_gates=['id','x','y','z','h','s','sdg','sx','sxdg','t','tdg','cx','reset','measure'],coupling_map=cm,initial_layout=phys,layout_method='sabre',routing_method='sabre',optimization_level=opt,seed_transpiler=seed)
 dp=list(tr.layout.final_index_layout()[:7]); txt=tprep.submission_text(tr,postselect=[(0,[tr.clbits[0]]),(0,[tr.clbits[1]])])
 ev=Eval(txt,dp); rr=run(ev,procs=1)
 return rr['loss'],rr['loss1'],rr['A1'],tr,dp,txt
# structured patches and random bijections for non-data wires
patches=[]
for r in range(0,5):
 for c in range(0,5): patches.append([6*r+c+i for i in range(7) if (i//6==0)])
# explicit connected-ish paths/patches; random start maps are also useful to Sabre.
patches += [[7,8,9,13,14,15,16],[0,1,2,6,7,8,12],[3,4,5,9,10,11,15],[20,21,22,26,27,28,32],[2,8,14,20,26,27,28],[5,11,17,23,29,30,31]]
rng=random.Random(20261024)
for _ in range(24): patches.append(rng.sample(range(N),7))
seen=set(); out=[]
for j,ds in enumerate(patches):
 if len(set(ds))<7: continue
 rest=[p for p in range(N) if p not in ds]; phys=ds+[10,11]+[p for p in rest if p not in (10,11)]
 key=tuple(phys)
 if key in seen:continue
 seen.add(key)
 try:
  loss,l1,a1,tr,dp,txt=compile_one(phys,9+j%5,1)
  out.append((loss,loss-l1,a1,tr.count_ops().get('cx',0),tr.depth(),j,dp,txt))
  print(j,'loss',loss,'l1',l1,'A1',a1,'cx',tr.count_ops().get('cx',0),'depth',tr.depth(),'dp',dp,flush=True)
 except Exception as e: print('ERR',j,e,flush=True)
out.sort(key=lambda x:x[0]);
for rank,x in enumerate(out[:10]):print('TOP',rank,x[:6],x[6])
if out:
 best=out[0];pathlib.Path('work/lanes/CC/cc_hm_best.qasm').write_text(best[7]);json.dump({'data_qubits':best[6],'loss2':best[0],'loss1':best[1],'A1':best[2],'cx':best[3],'depth':best[4]},open('work/lanes/CC/cc_hm_best.json','w'),indent=2)
json.dump([dict(loss=x[0],loss2=x[1],A1=x[2],cx=x[3],depth=x[4],idx=x[5],data=x[6]) for x in out],open('work/lanes/CC/search.json','w'),indent=2)
