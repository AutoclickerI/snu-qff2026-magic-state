"""Zero-width-aware cubic-gradient proposals, ranked only by full all orders."""
import sys,re,json,math,copy
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import acceptance as a
import zero_idle,moments_gradient as mg,numpy as np
from ortools.sat.python import cp_model

def reference(text):
 ev=a.C.exact2.Eval(text,a.C.D);lines=text.splitlines();pos=[i for i,s in enumerate(lines)if s.startswith('// DETECTOR')];rows=[lines[i]for i in pos]
 native=[int(re.search(r'DETECTOR line (\d+)',lab)[1])-1 for lab in ev.m.labels if lab.startswith('DETECTOR line ')]
 active=[i for i,x in enumerate(ev.e.projs)if x[:2]!=(0,0)];inactive=[i for i in range(len(rows))if i not in active];perm=inactive[:16]+active+inactive[16:];last=int(re.findall(r'measure q\[\d+\] -> c\[(\d+)\];',text)[-1]);assert 16+len(active)<53
 for i,old in enumerate(perm):lines[pos[i]]=rows[native[old]]+f' c[{last}] c[{last}]'
 return '\n'.join(lines)+'\n'

def proposals(c,seedname):
 ev=zero_idle.evaluate(reference(a.C.textof(c)),a.C.D);base,grad=mg.evaluate(ev);per={}
 for i,u in enumerate(c['u']):
  for q in u.qs:per.setdefault(q,[]).append(i)
 old=c['t'];R=c['meta']['R'];mx=max(old);by=np.bincount(ev.fch,weights=ev.fp*grad,minlength=len(ev.m.chans));byA=np.bincount(ev.fch,weights=ev.fp*(1-ev.a_single),minlength=len(ev.m.chans))
 for radius in (1,2,4):
  for scope in ('all','A','late_data'):
   for floor in (.5006,.504):
    m=cp_model.CpModel();ts=[m.NewIntVar(max(0,t-radius),min(mx,t+radius),f't{i}')for i,t in enumerate(old)]
    for i,(u,t) in enumerate(zip(c['u'],old)):
     if t>=R or(scope=='A'and not(set(u.qs)&set(a.C.A)and t>=32))or(scope=='late_data'and t<25):m.Add(ts[i]==t)
    ends={}
    for q,seq in per.items():
     for i,j in zip(seq,seq[1:]):m.Add(ts[j]>ts[i]);ends[q,old[i]+1]=(i,j)
     ends[q,old[seq[-1]]+1]=(seq[-1],None)
    loss=[];acc=[]
    for ci,ch in enumerate(ev.m.chans):
     if ch['gap']is None:continue
     q,start,n=ch['gap'];i,j=ends[q,start];end=mx+1 if j is None else ts[j];delta=end-ts[i]-1-n
     assert(mx+1 if j is None else old[j])-old[i]-1==n
     dp=-.75*math.log1p(-4e-3/3)*(1-4e-3/3)**n;ix=np.flatnonzero(ev.fch==ci)
     gl=by[ci]/ch['prob']if ch['prob']else float(np.mean(grad[ix]));ga=byA[ci]/ch['prob']if ch['prob']else float(np.mean(1-ev.a_single[ix]));loss.append(round(gl*dp*1e13)*delta);acc.append(round(ga*dp*1e10)*delta)
    m.Add(sum(acc)<=round((-math.log(floor)+math.log(base['exp_minus_A1']))*1e10));m.Minimize(sum(loss));s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=3;s.parameters.cp_model_presolve=False;status=s.Solve(m)
    if status not in(cp_model.FEASIBLE,cp_model.OPTIMAL):continue
    x=a.C.clone(c);x['t']=[s.Value(t)for t in ts]
    try:x=a.d.normalize(x)
    except AssertionError:continue
    yield f'{seedname}_{scope}_{radius}_{int(floor*10000)}',x,dict(family='zero_idle_feedback',parent=seedname,radius=radius,scope=scope,proxy_floor=floor,predicted=base['total']+s.ObjectiveValue()/1e13,gradient_base=base,changes=sum(t!=u for t,u in zip(old,x['t'])))
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('stems',nargs='+');p.add_argument('--workers',type=int,default=12);p.add_argument('--label',default='feedback');args=p.parse_args()
 def allitems():
  for st in args.stems:
   path=Path(st);c=a.d.normalize(a.C.read(path));yield from proposals(c,path.name)
 a.batch(allitems(),args.label,args.workers)
