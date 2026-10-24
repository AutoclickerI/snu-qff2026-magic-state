"""Budget-aware protection families: replace, share helpers, split windows, cross seeds."""
import sys,random,itertools,json,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import acceptance as a
C=a.C;d=a.d

def echo(c,q,h,axis,start,end,reuse=False):
 c=C.clone(c);ts=c['t'];us=c['u'];bit=C.bit(c)
 assert abs(q//6-h//6)+abs(q%6-h%6)==1 and end-start>=(2 if reuse else 3)
 busy={t for u,t in zip(us,ts) if h in u.qs}
 assert not any(t in busy for t in range(start,end+1))
 x1=start if reuse else start+1;x2=end-1
 assert x1<x2 and not any(q in u.qs and t in (x1,x2) for u,t in zip(us,ts))
 prev=[i for i,u in enumerate(us)if h in u.qs and ts[i]<start];nxt=[i for i,u in enumerate(us)if h in u.qs and ts[i]>end]
 assert not prev or us[prev[-1]].name in ('MX','MEASURE')
 assert not nxt or us[nxt[0]].name in ('MX','MEASURE','RX','RESET')
 if reuse:
  assert prev and us[prev[-1]].name==('MEASURE'if axis=='X'else'MX')
  prior=a.bits(' '.join(us[prev[-1]].lines))[0]
 else:
  init=[f'reset q[{h}];']+([f'h q[{h}];']if axis=='Z'else[]);us.append(C.Unit(init));ts.append(start)
 edge=f'cx q[{q}],q[{h}];'if axis=='X'else f'cx q[{h}],q[{q}];'
 meas=[f'measure q[{h}] -> c[{bit}];']
 if axis=='Z':meas=[f'h q[{h}];']+meas+[f'h q[{h}];']
 for lines,t in [([edge],x1),([edge],x2),(meas,end)]:us.append(C.Unit(lines));ts.append(t)
 c['tail'].append(f'// DETECTOR c[{bit}]'+(f' c[{prior}]'if reuse else''))
 return d.normalize(c)

def all_free(c,targets=None,reuse=False):
 targets=targets or C.D+[4,15,16]+C.A
 for q in sorted(set(targets)):
  seq=[i for i,u in enumerate(c['u'])if q in u.qs]
  for ia,ib in zip(seq,seq[1:]):
   lo,hi=c['t'][ia]+1,min(c['t'][ib]-1,c['meta']['R']-1)
   if hi-lo<2 or hi<18:continue
   for h in range(36):
    if abs(q//6-h//6)+abs(q%6-h%6)!=1:continue
    hs=[i for i,u in enumerate(c['u'])if h in u.qs];busy={c['t'][i]for i in hs};free=[];st=None
    for t in range(lo,hi+2):
     if t<=hi and t not in busy:
      if st is None:st=t
     elif st is not None:
      if t-st>=(3 if reuse else 4):free.append((st,t-1))
      st=None
    for aa,bb in free:
     windows={(aa,bb)}
     if bb-aa>=7:windows|={(aa,aa+3),(bb-3,bb),(aa,(aa+bb)//2),((aa+bb)//2+1,bb)}
     for start,end in sorted(windows):
      for axis in ('X','Z'):
       try:x=echo(c,q,h,axis,start,end,reuse)
       except (AssertionError,ValueError):continue
       yield x,dict(family='shared_helper'if reuse else'echo_window',q=q,h=h,axis=axis,window=[start,end],reuse=reuse)

def add_compatible(c,ee):
 q,h,axis,aa,bb,*_=ee
 try:return echo(c,q,h,axis,aa,bb),[q,h,axis,aa,bb]
 except (AssertionError,ValueError):pass
 # Preserve the requested interval when native slots permit; otherwise use
 # the longest compatible subwindow, with all-orders as the final arbiter.
 opts=[]
 for start in range(aa,min(bb-2,aa+8)+1):
  for end in range(bb,max(start+2,bb-8),-1):
   try:x=echo(c,q,h,axis,start,end)
   except (AssertionError,ValueError):continue
   opts.append((end-start,-abs(start-aa)-abs(end-bb),x,[q,h,axis,start,end]))
 if not opts:return None,None
 _,_,x,desc=max(opts,key=lambda v:v[:2]);return x,desc

def cross_seeds():
 root=a.H.parents[2]
 for nm in ['A44_timing_10','A44_port_10','A44_feedback_0','full_timing_0']:
  st=root/'work/lanes/SEPBC/v31'/nm
  if not st.with_suffix('.qasm').exists():continue
  c=d.normalize(C.read(st));yield nm+'_base',c,dict(family='external_seed',source=str(st))
  # All 8 one-drop and all 28 two-drop protection sets, plus full set.
  subsets=[set()]+[{i}for i in range(8)]+[set(z)for z in itertools.combinations(range(8),2)]
  # Seed family diversity; fuller sweep is applied after first all-orders rank.
  if nm not in ('A44_timing_10','A44_port_10'):subsets=[set(),{0},{4},{5},{4,5}]
  for drop in subsets:
   x=C.clone(c);desc=[]
   for i,e in enumerate(a.ECHO):
    if i in drop:continue
    out,rec=add_compatible(x,e)
    if out is None:desc.append(dict(unavailable=e));continue
    x=out;desc.append(rec)
   yield nm+'_drop'+('none'if not drop else'_'.join(map(str,sorted(drop)))),x,dict(family='protection_seed_cross',source=str(st),drop=sorted(drop),echoes=desc)

if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('mode');p.add_argument('--workers',type=int,default=14);args=p.parse_args()
 if args.mode=='cross':a.batch(cross_seeds(),'cross',args.workers)
