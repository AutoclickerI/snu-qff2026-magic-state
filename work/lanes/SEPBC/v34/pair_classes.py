"""Unchanged exact2.run physical-pair ledger; arbitrary Python detector masks."""
from design import *
from model import Basis
import collections
for name in sys.argv[1:]:
 st=V/name;c=json.loads(st.with_suffix('.plan.json').read_text());txt=st.with_suffix('.qasm').read_text();ev=exact2.Eval(txt,c['meta']['data_qubits']);R=c['meta']['R'];flat=[(l,o.get('tag','prefix'))for o in c['ops']for l in o['lines']];at=0;tags={}
 for li,line in enumerate(txt.splitlines(),1):
  s=line.strip()
  if not s or s.startswith(('//','barrier','OPENQASM','include','qreg','creg')):continue
  assert s==flat[at][0];tags[li]=flat[at][1];at+=1
 regions=[]
 for j,ch in enumerate(ev.m.chans):
  lab=ev.chan_label(j);regions.append(('pre_round_idle'if ch['gap'][1]+ch['gap'][2]<=R else'round')if ch['gap']is not None else tags[lab['line']])
 bas=Basis();indices=[];constraints=[]
 for i,(x,z,coef)in enumerate(ev.e.projs):
  co=bas.express(x|(z<<ev.e.r))
  if co is None:bas.add(x|(z<<ev.e.r));indices.append(i)
  else:
   rel=1<<i
   for j,bi in enumerate(indices):
    if co>>j&1:rel^=1<<bi
   constraints.append(rel)
 old=ev.e.ntable;ev.e.ntable=lambda s,d:(0.,None)if any((int(d)&h).bit_count()%2 for h in constraints)else old(s,d)
 r=exact2.run(ev,2,keep_thr=0);pairs=collections.Counter();examples={}
 for value,i,j,n,acc in r['big']:
  key=' x '.join(sorted([regions[int(ev.fch[i])],regions[int(ev.fch[j])]]));pairs[key]+=value
  if value>examples.get(key,[0])[0]:examples[key]=[value,ev.fault_label(i),ev.fault_label(j)]
 expected=json.loads(st.with_suffix('.screen.json').read_text())['second'];assert abs(r['loss2']-expected)<1e-15,(r['loss2'],expected)
 out=dict(second=r['loss2'],pair_classes=dict(pairs.most_common()),examples=examples,method='Unchanged exact2.run second order with exact dependent-detector rejection cache; no detector dropped.');st.with_suffix('.pairs.json').write_text(json.dumps(out,indent=2));print(name,json.dumps(out['pair_classes']),flush=True)
