import os,sys,itertools,json,argparse
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from ortools.sat.python import cp_model
P0={0,1,2,3,4,6,7,8,9,10,13,14,15,19,20}; PRE0=[0,20,7,4,3,15,8]
def tf(rc,k):
 r,c=rc;return [(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][k]
def nb(q):
 r,c=divmod(q,6);return [v for v in (q-6 if r else -1,q+6 if r<5 else -1,q-1 if c else -1,q+1 if c<5 else -1) if v>=0]
EDGES=[(u,v) for u in range(36) for v in nb(u)]
def paths(q,maxh,P):
 out=[]
 def rec(p):
  out.append(p[:])
  if len(p)-1>=maxh:return
  for v in nb(p[-1]):
   if v not in p and v in P:rec(p+[v])
 rec([q]);return out
def solve(P,rel,PRE,tag,a):
 F=set(range(36))-P; AV=sorted(F|rel);m=cp_model.CpModel();dom={'d':sorted(P),'a':AV,'b':AV,'c':AV}
 x={(k,i,q):m.NewBoolVar(f'{k}{i}_{q}') for k in 'dabc' for i in range(7) for q in dom[k]};pos={};col={}
 for k in 'dabc':
  for i in range(7):
   m.AddExactlyOne(x[k,i,q] for q in dom[k]);pos[k,i]=m.NewIntVar(0,35,f'{k}{i}');m.Add(pos[k,i]==sum(q*x[k,i,q] for q in dom[k]));col[k,i]=m.NewBoolVar(f'col{k}{i}');m.Add(col[k,i]==sum(((q//6+q%6)&1)*x[k,i,q] for q in dom[k]))
 for q in range(36):m.AddAtMostOne(x[k,i,q] for k in 'dabc' for i in range(7) if q in dom[k])
 for i in range(7):
  for k,l in [('d','a'),('d','b'),('b','c')]:m.AddAllowedAssignments([pos[k,i],pos[l,i]],EDGES);m.Add(col[k,i]+col[l,i]==1)
 # Each block is its own connected 7-cell shape.
 for root in 'abc':
  mem={q:sum(x[root,i,q] for i in range(7) if q in dom[root]) for q in range(36)};flow={(u,v):m.NewIntVar(0,7,f'f{root}{u}_{v}') for u,v in EDGES}
  for (u,v),z in flow.items():m.Add(z<=7*mem[u]);m.Add(z<=7*mem[v])
  for q in range(36):m.Add(sum(flow[q,v]-flow[v,q] for v in nb(q))==7*(x[root,0,q] if q in dom[root] else 0)-mem[q])
 # Data walk endpoints in P; any P cell used by a path is unavailable as another endpoint.
 pv=[];chosen=[]
 for i,q0 in enumerate(PRE):
  ps=paths(q0,a.hops,P);vv=[m.NewBoolVar(f'p{i}_{j}') for j in range(len(ps))];m.AddExactlyOne(vv);m.Add(pos['d',i]==sum(p[-1]*v for p,v in zip(ps,vv)));pv.append(vv);chosen.append(ps)
  for j in range(7):
   if i==j:continue
   for p,v in zip(ps,vv):
    for q in p:m.Add(pos['d',j]!=q).OnlyEnforceIf(v)
 hops=[sum((len(p)-1)*v for p,v in zip(ps,vv)) for ps,vv in zip(chosen,pv)];R=m.NewIntVar(33,80,'R')
 # Lower bound includes 3 CX steps per physical data hop and minimum encoder depths.
 for h in hops:m.Add(R>=33+3*h)
 m.Minimize(10000*R+100*sum(hops))
 s=cp_model.CpSolver();s.parameters.max_time_in_seconds=a.seconds;s.parameters.num_workers=a.workers;s.parameters.random_seed=a.seed
 st=s.Solve(m)
 if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE): print('NO',tag,s.StatusName(st),flush=True); return None
 d={k:[s.Value(pos[k,i]) for i in range(7)] for k in 'dabc'};d.update(P=sorted(P),F=sorted(F),released=sorted(rel),pre_transform=tag,R_lb=s.Value(R),hops=sum(s.Value(h) for h in hops),moves=[next(p for p,v in zip(ps,vv) if s.Value(v)) for ps,vv in zip(chosen,pv)])
 return d
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=20);ap.add_argument('--workers',type=int,default=8);ap.add_argument('--hops',type=int,default=5);ap.add_argument('--count',type=int,default=100);ap.add_argument('--out',default='sep');ap.add_argument('--seed',type=int,default=0);a=ap.parse_args();n=0
 for k in range(8):
  raw=[tf((q//6,q%6),k) for q in P0];mr=min(r for r,c in raw);mc=min(c for r,c in raw);h=max(r for r,c in raw)+1;w=max(c for r,c in raw)+1
  for tr in range(6-h+1):
   for tc in range(6-w+1):
    mp=lambda rc:(rc[0]-mr+tr,rc[1]-mc+tc);P={r*6+c for r,c in map(mp,raw)};PRE=[r*6+c for r,c in map(lambda q:mp(tf((q//6,q%6),k)),PRE0)];rel={r*6+c for q in (13,19) for r,c in [mp(tf((q//6,q%6),k))]};tag=f's{k}_r{tr}_c{tc}'
    d=solve(P,rel,PRE,tag,a)
    if d:
     f=f'{a.out}_{n:03d}.json';open(f,'w').write(json.dumps(d,indent=2)+'\n');print(f,tag,'R',d['R_lb'],'hops',d['hops'],'rel',d['released'],'d',d['d'],'a',d['a'],'b',d['b'],'c',d['c'],flush=True);n+=1
     if n>=a.count:return
if __name__=='__main__':main()
