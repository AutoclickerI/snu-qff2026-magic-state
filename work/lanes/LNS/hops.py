from moves import *
PAIRS=[(4,10),(15,16),(8,9),(9,15),(15,21),(16,22)]
def hop_ids(base,src,dst,occ=0):
 cutoff=-1
 if (src,dst)==(4,10):cutoff=next(t for u,t in zip(base['u'],base['t'])if any('-> c[8];'in s for s in u.lines))
 if (src,dst)in [(8,9),(9,15)]:cutoff=next(t for u,t in zip(base['u'],base['t'])if any('-> c[9];'in s for s in u.lines))
 return [i for i,(u,t)in enumerate(zip(base['u'],base['t']))if u.name=='CX'and set(u.qs)=={src,dst}and cutoff<t<base['meta']['R']][2*occ:2*occ+2]
def moves(base):
 for src,dst,occ in base['meta'].get('lns_transfers',[(a,b,0)for a,b in PAIRS]):
  ids=hop_ids(base,src,dst,occ)
  assert len(ids)==2,(src,dst,ids)
  i,j=ids;init=max((k for k in range(i)if dst in base['u'][k].qs),default=-1)
  if base['u'][init].name not in ('RESET','RX','MEASURE','MX'):continue
  # Switch the transfer destination's known basis, and repair all subsequent
  # single-cell watches of its vacated source through the next reset.
  for mode in ['reset0','resetplus','measure0','reuseplus']:
   c=clone(base);du=c['u'][init];b=bit(c);drop=[];plus=mode in ('resetplus','reuseplus')
   if du.name=='MX' and mode!='reuseplus':continue
   if du.name=='MEASURE':
    oldbit=int(re.findall(r'c\[(\d+)\]',' '.join(du.lines))[0]);delbit(c,oldbit)
   if mode=='reset0':c['u'][init]=Unit([f'reset q[{dst}];'])
   elif mode=='resetplus':c['u'][init]=Unit([f'reset q[{dst}];',f'h q[{dst}];'])
   elif mode=='measure0':c['u'][init]=Unit([f'measure q[{dst}] -> c[{b}];']);adddet(c,b)
   else:
    prev=[k for k in range(init)if dst in c['u'][k].qs]
    if du.name=='MX':c['u'][init]=Unit(du.lines[:2]+[f'h q[{dst}];'])
    elif prev and c['u'][prev[-1]].name=='MX':
     k=prev[-1];c['u'][k]=Unit(c['u'][k].lines[:2]+[f'h q[{dst}];']);drop=[init]
    else:continue
   for k,(a,z)in zip(ids,[(dst,src),(src,dst)]if plus else [(src,dst),(dst,src)]):c['u'][k]=Unit([f'cx q[{a}],q[{z}];'])
   for k in range(j+1,len(c['u'])):
    v=c['u'][k]
    if src not in v.qs:continue
    if v.name in ('RESET','RX','CX'):break
    if v.name in ('MEASURE','MX'):
     bb=int(re.findall(r'c\[(\d+)\]',' '.join(v.lines))[0])
     if plus:c['u'][k]=Unit([f'h q[{src}];',f'measure q[{src}] -> c[{bb}];',f'h q[{src}];'])
     else:c['u'][k]=Unit([f'measure q[{src}] -> c[{bb}];'])
   for k in sorted(drop,reverse=True):del c['u'][k];del c['t'][k]
   yield c,dict(family='hop',move='destination_basis',edge=[src,dst],mode=mode)
  # Move a complete transfer and its destination preparation together.
  for delta in [-6,-3,-2,-1,1,2,3,6]:
   c=clone(base);targets={k:max(0,c['t'][k]+delta)for k in [init,i,j]}
   yield retime(c,targets),dict(family='hop',move='chain_shift',edge=[src,dst],delta=delta)
 # Reroute data-15 through 21 (then22), completing before data-8 enters21.
 if base['meta'].get('lns_transfers'):return
 c=clone(base);removed=set();b=bit(c)
 oldpath=[]
 for edge in [{15,16},{16,22}]:
  oldpath.extend([i for i,(u,t)in enumerate(zip(c['u'],c['t']))if u.name=='CX'and 28<=t<c['meta']['R'] and set(u.qs)==edge][:2])
 if len(oldpath)==4:
  for k in oldpath:removed.add(k)
  # Existing initialization of 21 is moved ahead of its first temporary use.
  iz=next(i for i,u in enumerate(c['u'])if u.lines[0].startswith('measure q[21]'))
  c['t'][iz]=28
  for q,t in [(21,33)]:c['u'].append(Unit([f'measure q[{q}] -> c[{b}];']));c['t'].append(t);adddet(c,b);b+=1
  # Original q15 watch cannot precede the first completed transfer.
  for i,u in enumerate(c['u']):
   if u.lines[0]=='measure q[15] -> c[47];':c['t'][i]=31
   if u.lines[0].startswith('measure q[22]'):c['t'][i]=30
  for a,z,t in [(15,21,29),(21,15,30),(21,22,31),(22,21,32)]:c['u'].append(Unit([f'cx q[{a}],q[{z}];']));c['t'].append(t)
  c['u']=[u for i,u in enumerate(c['u'])if i not in removed];c['t']=[t for i,t in enumerate(c['t'])if i not in removed]
  order=sorted(range(len(c['u'])),key=lambda i:(c['t'][i],i));c['u']=[c['u'][i]for i in order];c['t']=[c['t'][i]for i in order]
  c['meta']['lns_transfers']=[(4,10,0),(15,21,0),(8,9,0),(9,15,0),(15,21,1),(21,22,0)]
  yield retime(c),dict(family='hop',move='reroute15_via21')

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--workers',type=int,default=8);ap.add_argument('--label',default='hops');a=ap.parse_args();batch(list(moves(read(a.stem))),a.label,a.workers)
