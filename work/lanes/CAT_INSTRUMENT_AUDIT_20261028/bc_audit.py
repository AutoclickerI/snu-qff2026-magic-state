import os,sys,json,itertools
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent;sys.path[:0]=[str(R/'work/lanes/END2_20261027'),str(R/'work/tools')]
from qtools.evaluator import frontend as f
from joint import emit
from tprep.qasm import to_stim
from tprep.exact import run
P=next((R/'work/lanes/NATIVE_CAT7_20261028/boundary').glob('cat7_opt_t11_m0_d21*.qasm'));ops,dets=f.parse_current(P.read_text());prefix=[o for o in ops if o.time<38];bits={o.bit for o in prefix if o.bit is not None};st,err=to_stim(emit(prefix,[r for r in dets if r<=bits]));assert not err
state,inv,records,_,w=run(st,36);B=[12,26,25,11,3,28,17];C=[18,27,24,5,4,29,23];S=[{0,2,4,6},{1,2,5,6},{3,4,5,6}]
def expect(axis,qs):
 p=state.stim.PauliString(state.n)
 for q in qs:p[w[q]]=axis
 return float(state.expectation(p,inv))
rows=[]
for g in S:rows.append({'kind':'X_BC','coords':sorted(g),'support':[B[i] for i in sorted(g)]+[C[i] for i in sorted(g) if i!=4],'value':expect('X',[B[i] for i in g]+[C[i] for i in g if i!=4])})
for g in S+[set(range(7))]:rows.append({'kind':'Z_B','coords':sorted(g),'support':[B[i] for i in sorted(g)],'value':expect('Z',[B[i] for i in g])})
for i in range(7):
 qs=[C[i]] if i==4 else [B[i],C[i]];rows.append({'kind':'Z_uncopied_C' if i==4 else 'Z_BC','index':i,'support':qs,'value':expect('Z',qs)})
out={'cut':38,'stem':str(P),'scope':'Literal ideal full prefix without conditioning; C4 already uncomputed by B3→C4@37. Expected resource X-space and Z checks, including logical zero.','rows':rows};(H/'bc_audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
