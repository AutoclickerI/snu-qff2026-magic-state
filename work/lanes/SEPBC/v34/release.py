from design import *
from collections import defaultdict
SOURCE_BITS={1:64,2:67,8:54,9:56,14:12,15:57,16:55}
def prefix(c):
 d=copy.deepcopy(c);ops=[]
 for o in d['ops']:
  if o.get('tag')=='encoder_a'and not any(f'-> c[{b}];'in' '.join(o['lines'])for b in(54,55)):continue
  if o.get('tag')in('round','decoder'):continue
  ops.append(o)
 return ops
def release(c):
 ops=prefix(c);ready={};es=[];last={}
 for o in ops:
  u=unit(o);t=max([last.get(q,-1)+1 for q in u.qs],default=0);es.append(t)
  for q in u.qs:last[q]=t
  sources=SOURCE_BITS if c['meta'].get('route')!='via14'else{**SOURCE_BITS,9:9,14:56}
  for q,b in sources.items():
   if f'measure q[{q}] -> c[{b}];'in o['lines']:ready[q]=dict(actual=o['t'],earliest=t,lines=o['lines'])
 assert set(ready)==set(A),ready
 return ready
if __name__=='__main__':
 c=getbase(0);r=release(c);(V/'release.json').write_text(json.dumps(r,indent=2));print(r)
