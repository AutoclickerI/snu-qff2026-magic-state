import os,sys,itertools,json,argparse,time
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from ortools.sat.python import cp_model
HERE=os.path.dirname(__file__); PRE0=[0,20,7,4,3,15,8]; P0={0,1,2,3,4,6,7,8,9,10,13,14,15,19,20}
def tf(rc,k):
 r,c=rc
 return [(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][k]
def nb(q):
 r,c=divmod(q,6);return [v for v in (q-6 if r else -1,q+6 if r<5 else -1,q-1 if c else -1,q+1 if c<5 else -1) if v>=0]
EDGES=[(u,v) for u in range(36) for v in nb(u)]
def solve(P,PRE,args,tag):
 F=set(range(36))-P

 m=cp_model.CpModel();dom={'d':list(range(36)),'a':list(range(36)),'b':sorted(F),'c':sorted(F)}
 x={(k,i,q):m.NewBoolVar(f'{k}{i}_{q}') for k in 'dabc' for i in range(7) for q in dom[k]};pos={};col={}
 for k in 'dabc':
  for i in range(7):
   m.AddExactlyOne(x[k,i,q] for q in dom[k]);pos[k,i]=m.NewIntVar(0,35,f'{k}{i}');m.Add(pos[k,i]==sum(q*x[k,i,q] for q in dom[k]));col[k,i]=m.NewBoolVar(f'c{k}{i}');m.Add(col[k,i]==sum(((q//6+q%6)&1)*x[k,i,q] for q in dom[k]))
 for q in range(36):m.AddAtMostOne(x[k,i,q] for k in 'dabc' for i in range(7) if q in dom[k])
 for i in range(7):
  for k,l in [('d','a'),('d','b'),('b','c')]:m.AddAllowedAssignments([pos[k,i],pos[l,i]],EDGES);m.Add(col[k,i]+col[l,i]==1)
 # connected A and BC via unit flow
 for roles,n,root in [('a',7,'a'),('bc',14,'b')]:
  mem={q:sum(x[k,i,q] for k in roles for i in range(7) if q in dom[k]) for q in range(36)}
  flow={e:m.NewIntVar(0,n,f'{roles}{e[0]}_{e[1]}') for e in EDGES}
  for (u,v),z in flow.items():m.Add(z<=n*mem[u]);m.Add(z<=n*mem[v])
  for q in range(36):m.Add(sum(flow[q,v]-flow[v,q] for v in nb(q))==n*(x[root,0,q] if q in dom[root] else 0)-mem[q])
 # data final endpoints and simple shortest routes in P, no endpoint collision
 def paths(q,maxh):
  out=[[q]]
  def rec(p):
   if len(p)-1>=maxh:return
   for v in nb(p[-1]):
    if v in p:continue
    pp=p+[v];out.append(pp);rec(pp)
  rec([q]);return out
 pv=[];pall=[]
 for i,q0 in enumerate(PRE):
  ps=paths(q0,args.hops);pall.append(ps);vv=[m.NewBoolVar(f'p{i}_{j}') for j in range(len(ps))];pv.append(vv);m.AddExactlyOne(vv);m.Add(pos['d',i]==sum(p[-1]*v for p,v in zip(ps,vv)))
  for j in range(7):
   if i==j:continue
   for p,v in zip(ps,vv):
    for q in p:m.Add(pos['d',j]!=q).OnlyEnforceIf(v)
 hops=[sum((len(p)-1)*v for p,v in zip(ps,vv)) for ps,vv in zip(pall,pv)]
 rh=m.NewIntVar(33,80,'R');
 for h in hops:m.Add(rh>=33+3*h)
 m.Minimize(10000*rh+100*sum(hops))
 s=cp_model.CpSolver();s.parameters.max_time_in_seconds=args.seconds;s.parameters.num_workers=args.workers;s.parameters.random_seed=0
 st=s.Solve(m)
 if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):return 0,s.StatusName(st)
 d={k:[s.Value(pos[k,i]) for i in range(7)] for k in 'dabc'};d.update(P=sorted(P),F=sorted(F),pre_transform=tag,R_lb=s.Value(rh),hops=sum(s.Value(h) for h in hops),moves=[next(p for p,v in zip(ps,vv) if s.Value(v)) for ps,vv in zip(pall,pv)])
 out=os.path.join(HERE,f'{args.out}_{tag}.json');open(out,'w').write(json.dumps(d,indent=2)+'\n');return 1,d

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=60);ap.add_argument('--workers',type=int,default=8);ap.add_argument('--hops',type=int,default=6);ap.add_argument('--out',default='lay');args=ap.parse_args()
 base=[(q//6,q%6) for q in sorted(P0)];res=[]
 for k in range(8):
  raw=[tf(rc,k) for rc in base];h=max(r for r,c in raw)+1;w=max(c for r,c in raw)+1
  for tr in range(6-h+1):
   for tc in range(6-w+1):
    mp=lambda rc: (rc[0]-min(r for r,c in raw)+tr,rc[1]-min(c for r,c in raw)+tc)
    P={r*6+c for r,c in map(mp,raw)};pr=[mp(tf((q//6,q%6),k)) for q in PRE0];PRE=[r*6+c for r,c in pr]
    tag=f's{k}_r{tr}_c{tc}'
    ok,v=solve(P,PRE,args,tag);print(tag,'ok',ok,v if not ok else {'R':v['R_lb'],'hops':v['hops'],'bd':sum(sum(u in set(range(36))-P for u in nb(q))>=2 for q in P)},flush=True)
if __name__=='__main__':main()
