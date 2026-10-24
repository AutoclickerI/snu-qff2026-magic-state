"""Finite idle-window echo, measured-Z initialization, and zero-check catalog."""
from common import *
import collections,itertools

def nb(q):return[v for v in range(36)if abs(v//6-q//6)+abs(v%6-q%6)==1]
def pulse_commutes(o,q,axis):
 if q not in o['qs']:return True
 n=o['name']
 if n=='CX':
  line=next(s for s in o['lines']if s.startswith('cx '));u,v=map(int,re.findall(r'q\[(\d+)\]',line));return(u==q)if axis=='X'else(v==q)
 if axis=='X':return n in('T','TDG','S','SDG','Z')
 return n in('X','SX','SXDG')

def echo_options(p):
 ops=p['ops'];end=max(o['t']for o in ops);targets=set(p['meta']['data_qubits'])
 for path in p['meta'].get('schedule',{}).get('paths',[]):targets.update(path)
 busy={q:{o['t']for o in ops if q in o['qs']}for q in range(36)};seq={q:sorted([o for o in ops if q in o['qs']],key=lambda o:o['t'])for q in range(36)};out=[];seen=set()
 for q in sorted(targets):
  live=[o['t']for o in seq[q]if o['name']not in('MEASURE','MX')]
  if not live:continue
  for h in nb(q):
   hs=seq[h];gaps=[]
   for j in range(len(hs)+1):
    prev=hs[j-1]if j else None;nxt=hs[j]if j<len(hs)else None
    if prev is not None and prev['name']not in('MEASURE','MX'):continue
    pivot_boundary=nxt is not None and nxt['name']=='MX'and nxt.get('init_frame',False)
    if nxt is not None and nxt['name']not in('RESET','RX')and not pivot_boundary:continue
    a=prev['t']+1 if prev else 0;b=nxt['t']-1 if nxt else end-1
    if b-a>=3:gaps.append((a,b,pivot_boundary))
   for axis in('X','Z'):
    blocked=[o['t']for o in seq[q]if not pulse_commutes(o,q,axis)];bounds=[-1]+sorted(set(blocked))+[end+1]
    for l,r in zip(bounds,bounds[1:]):
     for a,b,pivot_boundary in gaps:
      if pivot_boundary and axis!='X':continue
      low=max(a+1,l+1,min(live)+1);high=min(b-1,r-1,end-2);free=[t for t in range(low,high+1)if t not in busy[q]and t not in busy[h]]
      if len(free)<2:continue
      choices={(free[0],free[-1])}
      if free[-1]-free[0]>=6:
       middle=(free[0]+free[-1])//2;left=[t for t in free if t<=middle];right=[t for t in free if t>middle]
       if len(left)>1:choices.add((left[0],left[-1]))
       if len(right)>1:choices.add((right[0],right[-1]))
      for first,last in choices:
       desc=dict(type='echo',q=q,h=h,axis=axis,init=first-1,first=first,last=last,measure=last+1)
       if pivot_boundary:desc['next_measured_pivot']=True
       key=(q,h,axis,first,last)
       if key in seen:continue
       seen.add(key);assert all(pulse_commutes(o,q,axis)for o in seq[q]if first<o['t']<last);out.append(desc)
 return out

def reuse_echo_options(p):
 ops=p['ops'];end=max(o['t']for o in ops);targets=set(p['meta']['data_qubits']);out=[];seen=set()
 for path in p['meta'].get('schedule',{}).get('paths',[]):targets.update(path)
 for q in sorted(targets):
  qs=sorted([o for o in ops if q in o['qs']],key=lambda o:o['t']);busy={o['t']for o in qs}
  for h in nb(q):
   hs=sorted([o for o in ops if h in o['qs']],key=lambda o:o['t'])
   for j,prev in enumerate(hs):
    if prev['name']not in('MEASURE','MX'):continue
    nxt=hs[j+1]if j+1<len(hs)else None
    if nxt is not None and nxt['name']not in('RESET','RX'):continue
    axis='X'if prev['name']=='MEASURE'else'Z';prior=int(re.search(r'c\[(\d+)\]',' '.join(prev['lines']))[1]);a=prev['t']+1;b=nxt['t']-1 if nxt else end-1
    blocked=[o['t']for o in qs if not pulse_commutes(o,q,axis)];bounds=[-1]+sorted(set(blocked))+[end+1]
    for lo,hi in zip(bounds,bounds[1:]):
     free=[t for t in range(max(a,lo+1),min(b-1,hi-1,end-2)+1)if t not in busy]
     if len(free)<2:continue
     pairs={(free[0],free[-1])}
     if len(free)>3:pairs|={(free[1],free[-1]),(free[0],free[-2])}
     for first,last in pairs:
      key=(q,h,axis,first,last,prior)
      if key in seen:continue
      seen.add(key);out.append(dict(type='echo',q=q,h=h,axis=axis,init=None,first=first,last=last,measure=last+1,reuse=True,prior=prior,prior_time=prev['t']))
 return out

def deferred_readout_options(p):
 ops=p['ops'];end=max(o['t']for o in ops);out=[]
 for meas in ops:
  if meas['region']!='data_hops'or meas['name']!='MEASURE':continue
  h=meas['qs'][0];prior=max((o for o in ops if h in o['qs']and o['t']<meas['t']),key=lambda o:o['t'])
  if prior['name']!='CX'or prior['qs'][1]!=h:continue
  q=prior['qs'][0]
  if q not in p['meta']['data_qubits']:continue
  after=[o['t']for o in ops if h in o['qs']and o['t']>meas['t']];limit=min(after)-2 if after else end-1
  free=[t for t in range(meas['t'],min(limit,end-2)+1)if not any(q in o['qs']and o['t']==t for o in ops)]
  if len(free)<2:continue
  for first,last in {(free[0],free[-1])}:
   if not all(pulse_commutes(o,q,'X')for o in ops if first<o['t']<last):continue
   record=int(re.search(r'c\[(\d+)\]',meas['lines'][0])[1]);out.append(dict(type='deferred_echo',q=q,h=h,axis='X',first=first,last=last,measure=last+1,prior_time=meas['t'],record=record))
 return out

def zero_options(p):
 ops=p['ops'];by=collections.defaultdict(list)
 for o in ops:by[o['t']].append(o)
 out=[];stop=p['meta']['R']
 for reg in('BC','A'):
  cells=p['meta']['B']+p['meta']['C']if reg=='BC'else p['meta']['A'];state={};seen=set();degree=0;starts={}
  for q in cells:
   own=[o for o in ops if o['region']==reg and q in o['qs']]
   if not own:continue
   ini=next((o for o in own if len(o['qs'])==1 and o['name']in('RESET','RX','MX','MEASURE')),None)
   if ini:starts[q]=(ini['t'],ini['name']in('RX','MX'))
   else:
    first=min(o['t']for o in own);prev=[o for o in ops if q in o['qs']and o['t']<first];pr=max(prev,key=lambda o:o['t']);assert pr['name']in('MEASURE','MX','H'),pr
    plus=pr['name']=='H'or(pr['name']=='MX'and pr['lines'][-1].startswith('h '));starts[q]=(pr['t'],plus)
  sites=[]
  for t in range(stop):
   for q,(st,plus)in starts.items():
    if st==t:
     state[q]=1<<degree if plus else 0
     if plus:degree+=1
     seen.add(q)
   for o in by[t]:
    if o['region']==reg and o['name']=='CX':u,v=o['qs'];state[v]^=state[u]
   busy={q for o in by[t]for q in o['qs']}
   for q in seen-busy:
    if state[q]==0 and any(q in o['qs']and o['name']=='CX'and o['t']>t for o in ops):sites.append((q,t))
  for q in sorted({q for q,t in sites}):
   ts=sorted(t for qq,t in sites if qq==q)
   for j,t in enumerate(ts):
    if j+1==len(ts)or ts[j+1]!=t+1:out.append(dict(type='zero_check',q=q,t=t,region=reg))
 return out

def catalog(p):
 out=echo_options(p)+reuse_echo_options(p)+zero_options(p)
 for i,o in enumerate(p['ops']):
  if o['name']=='RESET':out.append(dict(type='measured_Z_init',index=i,q=o['qs'][0],t=o['t'],region=o['region']))
 for i,d in enumerate(out):d['id']=f'g{i:03d}'
 return out

def apply(p,actions):
 p=copy.deepcopy(p);b=bit(p);ops=p['ops'];chosen=[]
 for d in actions:
  if d['type']=='deferred_echo':
   q,h=d['q'],d['h'];ms=[o for o in ops if o['name']=='MEASURE'and o['qs']==[h]and o['t']==d['prior_time']and f'c[{d["record"]}]'in o['lines'][0]];assert len(ms)==1;ms[0]['t']=d['measure']
   for t in(d['first'],d['last']):ops.append(dict(t=t,name='CX',qs=[q,h],lines=[f'cx q[{q}],q[{h}];'],region='protection'))
   chosen.append(d);continue
  if d['type']=='echo':
   q,h=d['q'],d['h'];axis=d['axis'];edge=[q,h]if axis=='X'else[h,q]
   init=['reset q[%d];'%h]+(['h q[%d];'%h]if axis=='Z'else[])
   meas=(['h q[%d];'%h]if axis=='Z'else[])+[f'measure q[{h}] -> c[{b}];']
   if not d.get('reuse'):ops.append(dict(t=d['init'],name='RESET'if axis=='X'else'RX',qs=[h],lines=init,region='protection'))
   elif axis=='Z':
    previous=[o for o in ops if o['name']=='MX'and f'c[{d["prior"]}]'in ' '.join(o['lines'])];assert len(previous)==1
    if previous[0]['lines'][-1]!=f'h q[{h}];':previous[0]['lines'].append(f'h q[{h}];')
   ops += [dict(t=d['first'],name='CX',qs=edge,lines=[f'cx q[{edge[0]}],q[{edge[1]}];'],region='protection'),dict(t=d['last'],name='CX',qs=edge,lines=[f'cx q[{edge[0]}],q[{edge[1]}];'],region='protection'),dict(t=d['measure'],name='MEASURE'if axis=='X'else'MX',qs=[h],lines=meas,region='protection',bit=b)]
  elif d['type']=='zero_check':
   q=d['q'];ops.append(dict(t=d['t'],name='MEASURE',qs=[q],lines=[f'measure q[{q}] -> c[{b}];'],region='protection',bit=b))
  else:
   o=ops[d['index']];assert o['name']=='RESET'and o['qs']==[d['q']]and o['t']==d['t'];o.update(name='MEASURE',lines=[f'measure q[{d["q"]}] -> c[{b}];'],bit=b)
  p['tail'].append(f'// DETECTOR c[{b}]'+(f' c[{d["prior"]}]'if d.get('reuse')else''));b+=1;chosen.append(d)
 for d in actions:
  if d['type']in('echo','deferred_echo'):assert all(pulse_commutes(o,d['q'],d['axis'])for o in ops if d['first']<o['t']<d['last'])
 p['meta']['protection_actions']=p['meta'].get('protection_actions',[])+chosen
 return p

if __name__=='__main__':
 base=Path(sys.argv[1]);p=load(base);acts=catalog(p);out=[]
 for d in acts:
  try:s=save(apply(p,[d]),base.name+'_'+d['id']);out.append(dict(stem=s.name,action=d))
  except AssertionError as e:out.append(dict(action=d,build_error=repr(e)))
 (H/(base.name+'.actions.json')).write_text(json.dumps(acts,indent=2));(H/(base.name+'.guard_candidates.json')).write_text(json.dumps(out,indent=2));print(base.name,len(acts),collections.Counter(a['type']for a in acts),flush=True)
