"""P76 shared native emitter and full finite-p rank; all outputs stay in ST1."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from common import *
import contextlib,io
OUT=H/'p76'
def commuting_precedence(m,ops,ts):
 for q in range(36):
  seq=[i for i,o in enumerate(ops)if q in unit(o).qs]
  m.AddNoOverlap([m.NewFixedSizeIntervalVar(ts[i],1,f'wire{q}_{i}')for i in seq])
  for ii,i in enumerate(seq):
   for j in seq[ii+1:]:
    u,v=unit(ops[i]),unit(ops[j]);pu=S.name_qs(ops[i]['lines'][0])[1];pv=S.name_qs(ops[j]['lines'][0])[1]
    commute=u.name==v.name=='CX'and pu[0]!=pv[1]and pu[1]!=pv[0]
    commute|=u.name in('T','TDG')and v.name=='CX'and pu[0]==pv[0]
    commute|=v.name in('T','TDG')and u.name=='CX'and pv[0]==pu[0]
    if not commute:m.Add(ts[j]>ts[i])
source=H/'sparse_engine/sparse_walsh.py';sys.path.insert(0,str(source.parent))
spec=importlib.util.spec_from_file_location('p76_sparse',source);sw=importlib.util.module_from_spec(spec);sys.modules[spec.name]=sw;spec.loader.exec_module(sw);sw.__file__=str(OUT/'sparse_walsh.py')
def rank(stem,procs=1):
 stem=Path(stem);text=stem.with_suffix('.qasm').read_text();md=json.loads(stem.with_suffix('.json').read_text());ev=exact2.Eval(text,md['data_qubits']);c1=float(ev.fp@ev.n_single)
 with stem.with_suffix('.allorders.log').open('w')as log,contextlib.redirect_stdout(log):r=sw.run(stem,72,True,procs)
 r['c1']=c1;r['sha256']=hashlib.sha256(text.encode()).hexdigest();stem.with_suffix('.allorders.json').write_text(json.dumps(r,indent=2));return {k:r[k]for k in('loss','acceptance','c1','seconds','sha256')}
def phase_profile(ops,pivots,cells,flag):
 # Exact local categorical phase classes, used only as proposal information.
 first={q:min(t for t,u,v in ops if q in(u,v))for q in cells};z={q:(i+1)|8 for i,q in enumerate(cells)};x={q:i+1 for i,q in enumerate(cells)};weights=[0]*8;bygate={}
 def add(zz,xx,w,gate=None):
  if not xx and bool(zz&8)!=bool(zz&7):
   weights[zz&7]+=w
   if gate is not None and (zz&7)!=0 and (zz&7)-1 in flag:bygate[gate]=bygate.get(gate,0)+w
 for t in range(max(t for t,u,v in ops),min(first.values())-1,-1):
  layer=[(u,v)for tt,u,v in ops if tt==t];busy={q for edge in layer for q in edge}
  for u,v in layer:
   for pu in range(4):
    for pv in range(4):
     if pu or pv:add((z[u]if pu&2 else 0)^(z[v]if pv&2 else 0),(x[u]if pu&1 else 0)^(x[v]if pv&1 else 0),1,(t,u,v))
  for q in cells:
   if q not in busy and first[q]<t:add(z[q],0,5);add(0,x[q],5);add(z[q],x[q],5)
  for u,v in layer:z[v]^=z[u];x[u]^=x[v]
  for q in pivots:
   if first[q]==t:add(z[q],0,15)
 return dict(vector_units=weights,blind=sum(weights[i+1]for i in flag),detected=weights[0]+sum(weights[i+1]for i in range(7)if i not in flag),flag_code_support=flag),bygate
