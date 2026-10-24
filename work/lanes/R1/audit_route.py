"""Independent resource and token audit of route.py witnesses; no solver use."""
import os,sys,json
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from route import nb
p=Path(sys.argv[1]);d=json.loads(p.read_text());physical=d['args'].get('physical',False);busy={};ops=[];tokens={};last={};frames={}
def op(t,qs,kind):
 for q in qs:
  assert (t,q) not in busy,(t,q,kind,busy.get((t,q)))
  busy[t,q]=kind
 ops.append((t,kind,list(qs)))
for key,v in d['tokens'].items():
 tokens[key]=v['pos'][0];frames[key]=set()
 for j,(u,w,t,e) in enumerate(zip(v['pos'],v['pos'][1:],v['times'],v['ends'])):
  if u==w:continue
  assert w in nb(u),(key,u,w)
  if physical:
   if not v['fast'][j]:op(v['target_start'][j],[w],f'init:{key}')
   op(t,[u,w],f'forward:{key}');op(t+1,[u,w],f'back:{key}')
  else:
   op(t,[w],f'init:{key}');op(t+1,[u,w],f'forward:{key}');op(t+2,[u,w],f'back:{key}')
 for i in []:pass
for i in range(7):
 aa,bb=d['tokens'][f'a{i}'],d['tokens'][f'b{i}'];dp=d['tokens'][f'd{i}'];da=d.get('data_at_A',[d['tokens'][f'd{j}']['pos'][-1] for j in range(7)])[i]
 assert aa['coupling']<bb['coupling'];assert aa['pos'][-1] in nb(da);assert bb['pos'][-1] in nb(dp['pos'][-1])
 op(aa['coupling'],[da,aa['pos'][-1]],f'roundA:{i}');op(bb['coupling'],[dp['pos'][-1],bb['pos'][-1]],f'roundB:{i}')
 op(aa['coupling']+1,[aa['pos'][-1]],f'MA:{i}');op(bb['coupling']+1,[bb['pos'][-1]],f'MB:{i}')
# Each unmeasured token occupies its current site; transfers cannot hit another live token.
for t,kind,qs in sorted(ops):
 if kind.startswith('init:'):
  assert qs[0] not in tokens.values(),(t,kind,qs,tokens)
 elif kind.startswith('forward:'):
  key=kind.split(':')[1];u,w=qs;assert tokens[key]==u;assert w not in tokens.values(),(t,kind,qs,tokens)
 elif kind.startswith('back:'):
  key=kind.split(':')[1];u,w=qs;assert tokens[key]==u;tokens[key]=w
 elif kind.startswith('MA:'):tokens.pop('a'+kind.split(':')[1])
 elif kind.startswith('MB:'):tokens.pop('b'+kind.split(':')[1])
assert [tokens[f'd{i}'] for i in range(7)]==[d['tokens'][f'd{i}']['pos'][-1] for i in range(7)]
out=dict(status='PASS',layout=str(p),physical=physical,ops=len(ops),R=d['R'],Rmax=d['Rmax'],last_cx=d['last_cx']);p.with_suffix('.audit.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
