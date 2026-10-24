from core import *
from ortools.sat.python import cp_model
import argparse,time
P0=set(D0)|{1,2,6,9,10,13,14,19}; FREE=set(range(36))-P0
us,dets=parse_source();prep=[u for u in us if u['region']=='prep'];lastinit={q:max(i for i,u in enumerate(prep) if u['qs']==[q] and u['stmts'][0].startswith(('reset','measure'))) for q in A+B+C};AE=sorted({tuple(u['qs']) for i,u in enumerate(prep) if len(u['qs'])==2 and set(u['qs'])<=set(A) and all(i>lastinit[q] for q in u['qs'])})
BCE=sorted({tuple(u['qs']) for u in prep if len(u['qs'])==2 and set(u['qs'])<=set(B+C)})
print('AE',AE,'BCE',BCE,flush=True)
def solve(seed,seconds,bcfree,cap=4):
 m=cp_model.CpModel();roles=A+B+C+D;pos={q:m.NewIntVar(0,35,f'p{q}') for q in roles};m.AddAllDifferent(list(pos.values()));adj=[(u,v) for u in range(36) for v in nb(u)]
 for u,v in AE+BCE+list(zip(D,A))+list(zip(D,B))+[(17,16)]:m.AddAllowedAssignments([pos[u],pos[v]],adj)
 for q in B+C:m.AddAllowedAssignments([pos[q]],[[v] for v in bcfree])
 dist=[];late=[]
 for i,q in enumerate(D):
  dd=m.NewIntVar(0,cap,f'dd{i}');m.AddAllowedAssignments([pos[q],dd],[(v,abs(v//6-D0[i]//6)+abs(v%6-D0[i]%6)) for v in range(36) if abs(v//6-D0[i]//6)+abs(v%6-D0[i]%6)<=cap]);dist.append(dd)
 # Penalize A sites occupied by data, which need relocation before preparation.
 for q in A:
  z=m.NewBoolVar(f'late{q}');m.AddAllowedAssignments([pos[q],z],[(v,int(v in D0)) for v in range(36)]);late.append(z)
 m.Minimize(10*sum(dist)+4*sum(late))
 s=cp_model.CpSolver();s.parameters.num_workers=2;s.parameters.max_time_in_seconds=seconds;s.parameters.random_seed=seed;s.parameters.cp_model_presolve=False
 status=s.Solve(m);out=dict(status=s.StatusName(status),seed=seed,seconds=s.WallTime(),bound=s.BestObjectiveBound())
 if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):out.update(placement={q:s.Value(v) for q,v in pos.items()},distance=[s.Value(v) for v in dist],obj=s.ObjectiveValue())
 return out
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,default=0);ap.add_argument('--seconds',type=int,default=60);ap.add_argument('--kind',default='released');a=ap.parse_args()
 domain=FREE if a.kind=='never' else FREE|{13,19}
 r=solve(a.seed,a.seconds,domain);(HERE/f'place_{a.kind}_{a.seed}.json').write_text(json.dumps(r,indent=2));print(r,flush=True)
