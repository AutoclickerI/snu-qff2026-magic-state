"""Exact pair sum by emitted operation provenance (including teleports)."""
from common import *
from model import Basis
import collections
stem=Path(sys.argv[1]);plan=json.loads(stem.with_suffix('.plan.json').read_text());ops=plan['ops'];flat=[(line,o.get('tag','unknown'))for o in ops for line in o['lines']];tags={};at=0
for li,line in enumerate(stem.with_suffix('.qasm').read_text().splitlines(),1):
 s=line.strip()
 if not s or s.startswith(('//','barrier','OPENQASM','include','qreg','creg')):continue
 assert s==flat[at][0],(li,s,flat[at]);tags[li]=flat[at][1];at+=1
assert at==len(flat)
ev=exact2.Eval(stem.with_suffix('.qasm').read_text(),plan['meta']['data_qubits']);bas=Basis();indices=[];constraints=[]
for i,(x,z,c)in enumerate(ev.e.projs):
 combo=bas.express(x|(z<<ev.e.r))
 if combo is None:bas.add(x|(z<<ev.e.r));indices.append(i)
 else:
  rel=1<<i
  for j,bi in enumerate(indices):
   if combo>>j&1:rel^=1<<bi
  constraints.append(rel)
oldnt=ev.e.ntable
ev.e.ntable=lambda s,d:(0.,None)if any((int(d)&h).bit_count()%2 for h in constraints)else oldnt(s,d)
r=exact2.run(ev,procs=4,third=False,keep_thr=0);R=plan['meta']['R'];data=set(plan['meta']['data_qubits'])
def region(ch):
 lab=ev.chan_label(ch);tag=tags.get(lab['line'],'unknown');start=int(lab['steps'].split('..')[0]);idle=lab['kind']=='idle'
 if start>=R:return 'round'
 if tag in('bc_check','bc_data','bc_read','a_data','round'):
  if idle:
   return 'data_idle'if set(lab['qubits'])<=data else 'A_prep'if set(lab['qubits'])<=set(A)else'BC_prep_moves'
  return 'round'
 if tag.startswith(('bc_','tele_'))or tag=='BC':return 'BC_prep_moves'
 if tag=='A'or tag.startswith('a_'):return 'A_prep'
 if tag=='prefix':return 'prefix_including_idle'
 if tag=='hop':return 'data_moves'
 return tag
pairs=collections.Counter();examples={}
for value,i,j,n,a in r['big']:
 key=' x '.join(sorted([region(ev.fch[i]),region(ev.fch[j])]))
 pairs[key]+=value
 if value>examples.get(key,[0])[0]:examples[key]=[value,ev.fault_label(i),ev.fault_label(j)]
out=dict(second=r['loss2'],pair_classes=dict(pairs.most_common()),examples=examples,method='Exact2 physical pairs assigned by emitted operation provenance; prefix class includes its long data-idle windows')
stem.with_suffix('.provenance_pairs.json').write_text(json.dumps(out,indent=2));append_result(stem.name,out,'Provenance-specific pair attribution, replacing broad physical-region heuristics.');print(json.dumps(out),flush=True)
