from core import *
import itertools,argparse

def adddet(c,b):c['tail'].append(f'// DETECTOR c[{b}]')
def delbit(c,b):
 tail=[]
 for l in c['tail']:
  if l.startswith('// DETECTOR'):
   bs=set(map(int,re.findall(r'c\[(\d+)\]',l)))-{b}
   if not bs:continue
   l='// DETECTOR '+' '.join(f'c[{x}]'for x in sorted(bs))
  tail.append(l)
 c['tail']=tail

def init_moves(base):
 for i,u in enumerate(base['u']):
  q=u.qs[0];t=base['t'][i]
  if u.name=='RX':
   # Check in initialized X basis, retaining postmeasurement |+>.
   c=clone(base);b=bit(c);c['u'].insert(i+1,Unit([f'h q[{q}];',f'measure q[{q}] -> c[{b}];',f'h q[{q}];']));c['t'].insert(i+1,t+1);adddet(c,b)
   yield retime(c),dict(family='init',move='check_rx',unit=i,q=q)
   prev=[j for j,v in enumerate(base['u'][:i])if q in v.qs]
   if prev and base['u'][prev[-1]].name=='MX':
    c=clone(base);j=prev[-1];v=c['u'][j]
    if len(v.lines)==2:c['u'][j]=Unit(v.lines+[f'h q[{q}];'])
    del c['u'][i];del c['t'][i]
    yield c,dict(family='init',move='reuse_mx',unit=i,q=q)
  if u.name=='RESET':
   c=clone(base);b=bit(c);c['u'][i]=Unit([f'measure q[{q}] -> c[{b}];']);adddet(c,b)
   yield c,dict(family='init',move='reset_to_measure',unit=i,q=q)
  if u.name=='MEASURE' and t<base['meta']['R']:
   b=int(re.findall(r'c\[(\d+)\]',u.lines[0])[0])
   if f'// DETECTOR c[{b}]' in base['tail']:
    c=clone(base);c['u'][i]=Unit([f'reset q[{q}];']);delbit(c,b)
    yield c,dict(family='init',move='measure_to_reset',unit=i,q=q)
  # Monitor a vacated cell immediately before reinitialization.
  if u.name in ('RESET','RX') and any(q in v.qs for v in base['u'][:i]):
   for axis in ['Z','X']:
    c=clone(base);b=bit(c);lines=[f'measure q[{q}] -> c[{b}];']
    if axis=='X':lines=[f'h q[{q}];']+lines
    c['u'].insert(i,Unit(lines));c['t'].insert(i,max(0,t-1));adddet(c,b)
    yield retime(c),dict(family='init',move='watch_before_reset',axis=axis,unit=i,q=q)
 # Random X-init records on B/C pivots propagated through Clifford suffix.
 piv=[i for i,u in enumerate(base['u'])if u.name=='RX'and u.qs[0]in B+C and base['t'][i]>=29]
 for subset in [[i]for i in piv]+[piv]:
  c=clone(base);idx=bit(c);inits={}
  for i in subset:
   q=c['u'][i].qs[0];c['u'][i]=Unit([f'h q[{q}];',f'measure q[{q}] -> c[{idx}];',f'h q[{q}];']);inits[i]=idx;idx+=1
   prev=[j for j,v in enumerate(c['u'][:i])if q in v.qs]
   if prev and c['u'][prev[-1]].name=='MX'and len(c['u'][prev[-1]].lines)==2:
    j=prev[-1];c['u'][j]=Unit(c['u'][j].lines+[f'h q[{q}];'])
  frames={q:[set(),set()]for q in range(36)};corr={}
  for i,u in enumerate(c['u']):
   q=u.qs[0]
   if i in inits:frames[q]=[set(),{inits[i]}];continue
   if u.name in ('RESET','RX'):frames[q]=[set(),set()]
   elif u.name=='CX':
    a,b=map(int,S.QRE.findall(u.lines[0]));frames[b][0]^=frames[a][0];frames[a][1]^=frames[b][1]
   elif u.name in ('MEASURE','MX'):
    b=int(re.findall(r'c\[(\d+)\]',' '.join(u.lines))[0]);corr[b]=frames[q][u.name=='MX'].copy()
   elif u.name=='H':frames[q].reverse()
  assert all(not any(frames[q])for q in D)
  for j,l in enumerate(c['tail']):
   if l.startswith('// DETECTOR'):
    bs=set(map(int,re.findall(r'c\[(\d+)\]',l)));ex=set()
    for b in bs:ex^=corr.get(b,set())
    c['tail'][j]='// DETECTOR '+' '.join(f'c[{b}]'for b in sorted(bs^ex))
  yield c,dict(family='init',move='mx_init_pivots',units=subset)

def phase_moves(base):
 # Enumerate all final Tdag relocation masks through the existing transfers.
 for mask in range(8):
  c=clone(base)
  for j,(src,dst)in enumerate([(4,10),(15,22),(8,21)]):
   i=next(i for i,u in enumerate(c['u'])if u.name=='TDG'and u.qs[0]in (src,dst))
   if mask>>j&1:c['u'][i]=Unit([f'tdg q[{dst}];']);c['t'][i]=c['meta']['R']-1
   else:
    c['u'][i]=Unit([f'tdg q[{src}];']);hopdst={4:10,15:16,8:9}[src]
    c['t'][i]=min(t for u,t in zip(base['u'],base['t'])if u.name=='CX'and set(u.qs)=={src,hopdst}and t>=28)-1
  # Retiming requires chronology after moving a gate across a transfer chain.
  order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],i));c['u']=[c['u'][i]for i in order];c['t']=[c['t'][i]for i in order]
  yield retime(c),dict(family='phase',move='tdg_mask',mask=mask)

def timing_moves(base,alltimes=False):
 pred,succ=S.build_dag(base['u']);ts=base['t']
 for i,u in enumerate(base['u']):
  # Analytically closed by depolarizing covariance when every other occupied
  # native layer remains present. HOPS phase relocation still runs separately.
  if u.name in ('T','TDG') and pred[i] and succ[i] and ts.count(ts[i])>1:continue
  lo=max((ts[j]+1 for j in pred[i]),default=0);hi=min((ts[j]-1 for j in succ[i]),default=max(ts))
  for t in (range(lo,hi+1)if alltimes else sorted({lo,hi,ts[i]-1,ts[i]+1})):
   if t==ts[i]or not lo<=t<=hi:continue
   c=clone(base);c['t'][i]=t
   yield c,dict(family='timing',move='single',unit=i,old=ts[i],new=t,op=u.lines)

def commute_moves(base):
 us=base['u'];ts=base['t']
 for i,a in enumerate(us):
  if a.name!='CX':continue
  for j in range(i+1,len(us)):
   b=us[j]
   if not commute(a,b):break
   if b.name!='CX'or not(set(a.qs)&set(b.qs)):continue
   if all(commute(b,x)for x in us[i+1:j]):
    c=clone(base);c['u'][i],c['u'][j]=c['u'][j],c['u'][i]
    yield retime(c),dict(family='commute',move='swap',units=[i,j],old=[ts[i],ts[j]],ops=[a.lines,b.lines])

def detector_moves(base):
 for i,l in enumerate(base['tail']):
  if not l.startswith('// DETECTOR'):continue
  c=clone(base);del c['tail'][i]
  yield c,dict(family='readout',move='drop_detector',index=i,line=l)
  bs=list(map(int,re.findall(r'c\[(\d+)\]',l)))
  if len(bs)==1:
   for axis in ['X','Z','XZ']:
    d=clone(c);d['tail'] += [f'// FRAME_{p}(0)'+(f' c[{bs[0]}]'if p in axis else '')for p in ['X','Z']]
    yield d,dict(family='readout',move='drop_frame',axis=axis,line=l)

def readout_moves(base):
 last={u.qs[0]:i for i,u in enumerate(base['u'])if u.name=='MEASURE'and base['t'][i]>=base['meta']['R']+1}
 occupied={17,16,19,25}
 edges=[(a,b)for a in last for b in last if a!=b and abs(a//6-b//6)+abs(a%6-b%6)==1 and base['t'][last[a]]==base['t'][last[b]]]
 for a,b in edges:
  c=clone(base);ia,ib=last[a],last[b];ba=int(re.findall(r'c\[(\d+)\]',c['u'][ia].lines[0])[0]);bb=int(re.findall(r'c\[(\d+)\]',c['u'][ib].lines[0])[0]);t=c['t'][ia]
  c['t'][ia]=c['t'][ib]=t+1;c['u'].append(Unit([f'cx q[{a}],q[{b}];']));c['t'].append(t)
  for j,l in enumerate(c['tail']):
   if l.startswith('// DETECTOR'):
    bits=set(map(int,re.findall(r'c\[(\d+)\]',l)))
    if bb in bits:bits^={ba}
    c['tail'][j]='// DETECTOR '+' '.join(f'c[{x}]'for x in sorted(bits))
  yield c,dict(family='readout',move='add_edge',edge=[a,b])
 for a,b in [(17,16),(19,25)]:
  c=clone(base);ia,ib=last[a],last[b];ba=int(re.findall(r'c\[(\d+)\]',c['u'][ia].lines[0])[0]);bb=int(re.findall(r'c\[(\d+)\]',c['u'][ib].lines[0])[0])
  i=max(i for i,u in enumerate(c['u'])if u.lines==[f'cx q[{a}],q[{b}];'])
  del c['u'][i];del c['t'][i]
  for j,l in enumerate(c['tail']):
   if l.startswith('// DETECTOR'):
    bits=set(map(int,re.findall(r'c\[(\d+)\]',l)))
    if bb in bits:bits^={ba}
    c['tail'][j]='// DETECTOR '+' '.join(f'c[{x}]'for x in sorted(bits))
  yield c,dict(family='readout',move='remove_edge',edge=[a,b])

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('mode');ap.add_argument('--stem',default='');ap.add_argument('--workers',type=int,default=8);ap.add_argument('--label');a=ap.parse_args();cs=[]
 for stem in ([a.stem]if a.stem else [str(ROOT/f'work/lanes/MAIN/v22{f}_c2c9')for f in ['h','w']]):
  c=read(stem)
  for fn in {'choices':[init_moves,phase_moves,readout_moves], 'timing':[timing_moves], 'commute':[commute_moves], 'detector':[detector_moves]}[a.mode]:cs.extend(fn(c))
 batch(cs,a.label or a.mode,a.workers)
