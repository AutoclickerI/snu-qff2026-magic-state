import sys,json
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path[:0]=[str(H),str(R/'work'),str(R/'work/lanes/me_layout')]
import gmodel,run_moves,verify,exact_proxy as ep
source=R/'work/lanes/me_layout/res_A1_9b_1792752451.json'
_,aa,o,_,name=json.loads(source.read_text())[0];m=run_moves.variant(name);a=verify.load_assign(aa)
x,y=ep.gmodel_probes(m,a,o);r=dict(source=str(source.relative_to(R))+'#0',old=m.proxy(a,o),second=ep.exact_loss(x,y),all_orders=ep.conditional_loss(x,y))
# Native v12 coupling/move/U times mapped onto the same GModel keys. This model
# necessarily uses GModel's uniform initial Bell stage; its actual delayed Bell
# prep/retained ancillas are represented separately by cycles.py.
from prefix import OPS,NPRE,nt,native
by={}
for i,(k,qs,b) in enumerate(OPS[NPRE:],NPRE):by.setdefault((native(k),qs),[]).append(nt[i])
# Repeated physical CNOTs: assign two-hop moves first, then the final-round keys.
assigned={};remaining={k:sorted(v) for k,v in by.items()}
for key in sorted(m.keys,key=lambda k:0 if k[0]=='M' else 1):
 qs=tuple(gmodel.P(q) for q in m.qubits_of(key,o));v=remaining['CX',qs]
 # U is the last copy of its Bell edge. Extras/couplings are also the final copy
 # when a move or Bell preparation shares the edge.
 t=v.pop(0 if key[0]=='M' else -1);assigned[key]=t-33
assert m.feasible(assigned,o)
xx,yy=ep.gmodel_probes(m,assigned,o);v=dict(source='v12 submitted coupling/U/move schedule mapped to GModel',old=m.proxy(assigned,o),second=ep.exact_loss(xx,yy),all_orders=ep.conditional_loss(xx,yy),limitation='GModel normalizes Bell preparations and resets retained ancillas; actual native v12 round is reference_cycle_proxy.json')
(H/'gmodel_reference.json').write_text(json.dumps(dict(v11=r,v12_normalized=v),indent=2));print(r,v)
