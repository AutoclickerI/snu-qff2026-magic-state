"""Expand shortcut CX into a physical measured bus and exact record frames."""
import json,re,collections
from pathlib import Path
from retime import run
from synth_resource import F
H=Path(__file__).resolve().parent
p=json.loads((H/'region89_k45_A0_safe.plan.json').read_text());d=json.loads((H/'r89_bus_d10.prep.json').read_text());R=p['meta']['R'];helper=2;remote=lambda e:abs(e[0]//6-e[1]//6)+abs(e[0]%6-e[1]%6)!=1
count=sum(remote(e)for layer in d['ops']for e in layer);depth=len(d['ops'])+3*count;start=R-depth-1;assert start>=0
ops=[o for o in p['ops']if o['region']!='BC'];bit=max(map(int,re.findall(r'c\[(\d+)\]','\n'.join(l for o in p['ops']for l in o['lines']))))+1

def add(t,name,qs,reg='BC',**kw):
 global bit
 q=qs[0];o=dict(t=t,name=name,qs=qs,region=reg,tag=reg,**kw)
 if name=='RESET':o['lines']=[f'reset q[{q}];']
 elif name=='CX':o['lines']=[f'cx q[{q}],q[{qs[1]}];']
 elif name=='MX':o.update(bit=bit,lines=[f'h q[{q}];',f'measure q[{q}] -> c[{bit}];',f'h q[{q}];']);bit+=1
 else:raise ValueError(name)
 ops.append(o)
for q in d['B']+d['C']:add(start,'MX'if q in d['pivots']else'RESET',[q],init_frame=q in d['pivots'])
t=start+1
for layer in d['ops']:
 rr=[e for e in layer if remote(e)];assert len(rr)<=1
 if rr:add(t,'RESET',[helper],reg='bus');base=t+1
 else:base=t
 for u,v in layer:
  if not remote((u,v)):add(base,'CX',[u,v])
  else:
   assert abs(u//6-helper//6)+abs(u%6-helper%6)==1 and abs(v//6-helper//6)+abs(v%6-helper%6)==1
   add(base,'CX',[u,helper],reg='bus');add(base+1,'CX',[helper,v],reg='bus');add(base+2,'MX',[helper],reg='bus',bus_control=u)
 t+=4 if rr else 1
assert t==R
frames={q:[set(),set()]for q in range(36)};corr={};reads={}
for o in sorted(ops,key=lambda o:o['t']):
 qs=o['qs'];q=qs[0];n=o['name']
 if o.get('init_frame'):frames[q]=[set(),{o['bit']}]
 elif n in ('RESET','RX'):frames[q]=[set(),set()]
 elif n=='CX':u,v=qs;frames[v][0]^=frames[u][0];frames[u][1]^=frames[v][1]
 elif 'bus_control'in o:
  u=o['bus_control'];frames[u][1]^={o['bit']}^frames[q][1];frames[q]=[set(),set()]
 elif n=='H':frames[q].reverse()
 elif o.get('read'):corr[o['bit']]=frames[q][n=='MX'].copy();reads[q]=o['bit']
 elif n in ('T','TDG'):assert not any(frames[q])
assert all(not any(frames[q])for q in p['meta']['data_qubits'])
det=[]
for k in ('A','B'):
 for g in F.ROWS:
  ds={reads[p['meta'][k][i]]for i in g}
  for i in g:ds^=corr[reads[p['meta'][k][i]]]
  det.append(ds)
for q in p['meta']['C']:det.append({reads[q]}^corr[reads[q]])
p['tail']=p['tail'][:-13]+['// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(ds))for ds in det];p['h']=[re.sub(r'creg c\[\d+\]',f'creg c[{bit}]',s)for s in p['h']];p['ops']=sorted(ops,key=lambda o:o['t']);p['meta'].update(resource_cx=sum(map(len,d['ops']))+count,resource_depth=depth,logical_resource_depth=len(d['ops']),bus_count=count,bus_helper=helper,cx=sum(o['name']=='CX'for o in ops),source_resource=str(H/'r89_bus_d10.prep.json'))
temp=H/'region89_bus_ordered';temp.with_suffix('.plan.json').write_text(json.dumps(p,indent=1));run(temp,'region89_bus');print('logical_depth',len(d['ops']),'expanded_depth',depth,'bus_count',count)
