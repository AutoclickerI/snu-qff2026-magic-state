import os,sys,json
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from packing import D,P,F,nb
p=Path(sys.argv[1]);r=json.loads(p.read_text());tokens=r['tokens'];busy={};occupied={};events=[]
def reserve(t,q,who):
 assert (t,q) not in occupied,(t,q,who,occupied.get((t,q)))
 occupied[t,q]=who
for key,v in tokens.items():
 assert v['pos'][0] in F
 active=[j for j,x in enumerate(v['mv']) if x]
 end=r['args']['horizon']+1 if key[0]=='o' else v['tc']+2
 arrivals=[32]+v['reset']
 departures=v['en']+[end]
 for j,q in enumerate(v['pos']):
  for t in range(arrivals[j],departures[j]):reserve(t,q,key)
 for j in active:
  u,w=v['pos'][j:j+2];t=v['ts'][j]
  assert w in nb(u)
  fast=v.get('fast',[0]*len(v['mv']))[j]
  if not fast:events.append((t-1,(w,),key+'.reset'))
  else:assert j==0 and t==33 and w in P-set(D)
  events += [(t,(u,w),key+'.move1'),(t+1,(u,w),key+'.move2')]
for i,q in enumerate(D):
 o,b=(tokens[f'{k}{i}'] for k in 'ob')
 for t in range(32,o['tc']+2):reserve(t,q,'d'+str(i))
 assert o['atD'] in nb(q)
 assert b['pos'][-1] in nb(o['atB'])
 assert b['tc']>=max(o['tc']+1,o['en'][-1])
 events += [(o['tc'],(q,o['atD']),'od'),(o['tc']+1,(q,),'md'),(b['tc'],(b['pos'][-1],o['atB']),'bo'),(b['tc']+1,(b['pos'][-1],),'mb')]
for q in P-set(D):reserve(32,q,'prefix')
for t,qs,who in events:
 for q in qs:
  assert (t,q) not in busy,(t,q,who,busy.get((t,q)))
  busy[t,q]=who
out=dict(passed=True,scope='post-prefix two-block token occupancy, reset and CX conflicts, adjacency, coupling order; C/preparation not certified',source=str(p),R=r['R'],Rmax=r['Rmax'],last_cx=r['last_cx'],moves=r['moves'])
p.with_suffix('.audit.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
