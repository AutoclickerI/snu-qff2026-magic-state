"""Deterministic factorized-state checks in existing idle slots; no reset substituted."""
import json,re,sys,copy,collections
from pathlib import Path
H=Path(__file__).resolve().parent

def add(stem,out):
 p=json.loads(Path(stem).with_suffix('.plan.json').read_text());ops=p['ops'];meta=p['meta'];by=collections.defaultdict(list)
 for o in ops:by[o['t']].append(o)
 # Track each BC wire's computational amplitude as a vector over independent input pivots.
 # X initialization frame is Z-only and cannot affect deterministic Z checks.
 state={};seen=set();degree=0;sites=[]
 for t in range(meta['R']):
  busy={q for o in by[t]for q in o['qs']}
  for o in by[t]:
   if o['region']!='BC':continue
   q=o['qs'][0]
   if o['name']in ('RESET','RX','MX'):
    state[q]=0;seen.add(q)
    if o['name']!='RESET':state[q]=1<<degree;degree+=1
   elif o['name']=='CX':state[o['qs'][1]]^=state[q]
  for q in seen-busy:
   if state[q]==0 and any(o['region']=='BC'and q in o['qs']and o['t']>t for o in ops):sites.append((q,t))
 # Keep the last opportunity per uninterrupted zero interval, reducing redundant measurements.
 chosen=[]
 for q in sorted({q for q,t in sites}):
  ts=sorted(t for qq,t in sites if qq==q)
  chosen.extend((q,t)for j,t in enumerate(ts)if j+1==len(ts)or ts[j+1]!=t+1)
 bit=max(map(int,re.findall(r'c\[(\d+)\]','\n'.join(s for o in ops for s in o['lines']))))+1
 for q,t in chosen:
  ops.append(dict(t=t,name='MEASURE',qs=[q],lines=[f'measure q[{q}] -> c[{bit}];'],region='BC',tag='BC',bit=bit,zero_check=True));p['tail'].append(f'// DETECTOR c[{bit}]');bit+=1
 p['h']=[re.sub(r'creg c\[\d+\]',f'creg c[{bit}]',s)for s in p['h']];p['meta']['zero_checks']=chosen;p['ops']=sorted(ops,key=lambda o:o['t']);used=sorted({q for o in ops for q in o['qs']});bar='barrier '+','.join(f'q[{q}]'for q in used)+';';lines=p['h'][:]
 for t in sorted({o['t']for o in ops}):
  layer=[o for o in ops if o['t']==t];busy=[q for o in layer for q in o['qs']];assert len(busy)==len(set(busy));lines += [s for o in layer for s in o['lines']]+[bar]
 lines+=p['tail'];out=H/out;out.with_suffix('.qasm').write_text('\n'.join(lines)+'\n');out.with_suffix('.json').write_text(json.dumps(p['meta'],indent=2));out.with_suffix('.plan.json').write_text(json.dumps(p,indent=1));print(out.name,chosen)
if __name__=='__main__':add(*sys.argv[1:])
