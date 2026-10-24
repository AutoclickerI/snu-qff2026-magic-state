from core import *
from ortools.sat.python import cp_model
import argparse,time

def solve(args):
 h=json.loads(Path(args.stage).read_text());init={int(k):v for k,v in h['init'].items()};hint={int(k):v for k,v in h['final'].items()}
 perm=h.get('perm',{'a':list(range(7)),'b':list(range(7))})
 for q,v in zip(D,D0):init[q]=v
 enc,ready=stage_prep(init)
 pre,_=parse_source();release={}
 for u in pre:
  if u['region']=='pre':
   for q in u['qs']:release[q]=max(release.get(q,0),u['t']+1)
 m=cp_model.CpModel();iv={q:[] for q in range(36)};T={};adj=[(u,v) for u in range(36) for v in nb(u)]
 R=m.NewIntVar(34,args.horizon,'R')
 for key,start in init.items():
  n=args.dhops if key in D else args.bhops;pos=[m.NewIntVar(0,35,f'p{key}_{j}') for j in range(n+1)];m.Add(pos[0]==start)
  if args.fixed:m.Add(pos[-1]==hint[key])
  else:m.AddHint(pos[-1],hint[key])
  moves=[];ts=[];ends=[];targetstart=[]
  for j in range(n):
   mv=m.NewBoolVar(f'm{key}_{j}');t=m.NewIntVar(33,args.horizon,f't{key}_{j}');e=m.NewIntVar(33,args.horizon+2,f'e{key}_{j}');r=m.NewIntVar(32,args.horizon,f'r{key}_{j}')
   m.AddAllowedAssignments([pos[j],pos[j+1],mv],[(u,v,1) for u,v in adj]+[(q,q,0) for q in range(36)])
   # Source remains reserved until after the teleport measurement / second data CX.
   m.Add(e==t+2*mv);m.Add(r==t-mv)
   if j:m.Add(t>=ts[-1]+(2 if key in D else 1)*moves[-1]);m.Add(mv<=moves[-1])
   moves.append(mv);ts.append(t);ends.append(e);targetstart.append(r)
  if key not in D:m.Add(ts[0]>=ready[key])
  m.Add(ts[-1]+(2 if key in D else 1)*moves[-1]<=R)
  arrivals=[0]+targetstart;departures=ends+[R+3]
  for j in range(n+1):
   # Zero-length no-move segments must not produce overlapping occupancy on the same site.
   if j<n:
    active=moves[j]
   else:active=m.NewConstant(1)
   # For skipped moves, carry the original segment's arrival forward.
   arr=m.NewIntVar(0,args.horizon,'arr')
   if j==0:m.Add(arr==0)
   else:m.Add(arr==targetstart[j-1]).OnlyEnforceIf(moves[j-1]);m.Add(arr==arrs[-1]).OnlyEnforceIf(moves[j-1].Not())
   if j==0:arrs=[]
   arrs.append(arr)
   size=m.NewIntVar(0,args.horizon+3,'size');m.Add(size==departures[j]-arr)
   for q in range(36):
    z=m.NewBoolVar('');m.Add(pos[j]==q).OnlyEnforceIf(z);m.Add(pos[j]!=q).OnlyEnforceIf(z.Not())
    both=m.NewBoolVar('');m.AddBoolAnd([z,active]).OnlyEnforceIf(both);m.AddBoolOr([z.Not(),active.Not()]).OnlyEnforceIf(both.Not())
    iv[q].append(m.NewOptionalIntervalVar(arr,size,departures[j],both,''))
  T[key]=dict(pos=pos,mv=moves,t=ts,e=ends)
 for q in range(36):
  if q not in init.values() and release.get(q,0):iv[q].append(m.NewFixedSizeIntervalVar(0,release[q],''))
  m.AddNoOverlap(iv[q])
 for u,v in list(zip(D,[A[i] for i in perm['a']]))+list(zip(D,[B[i] for i in perm['b']]))+list(zip(B,C))+[(17,16),(19,25)]:m.AddAllowedAssignments([T[u]['pos'][-1],T[v]['pos'][-1]],adj)
 cost=sum(sum(v['mv'])*(3 if q in D else 1) for q,v in T.items());m.Minimize(R*1000+cost)
 s=cp_model.CpSolver();s.parameters.num_workers=args.workers;s.parameters.max_time_in_seconds=args.seconds;s.parameters.random_seed=args.seed;s.parameters.cp_model_presolve=False
 def result(cb):return dict(R=cb.Value(R),init=init,ready=ready,perm=perm,tokens={q:dict(pos=[cb.Value(v) for v in t['pos']],moves=[cb.Value(v) for v in t['mv']],times=[cb.Value(v) for v in t['t']]) for q,t in T.items()},args=vars(args),status='FEASIBLE')
 class CB(cp_model.CpSolverSolutionCallback):
  def on_solution_callback(self):
   o=result(self);(HERE/(args.out+'.json')).write_text(json.dumps(o,indent=2));print('solution',self.ObjectiveValue(),self.WallTime(),flush=True)
 st=s.Solve(m,CB());receipt=dict(status=s.StatusName(st),stats=s.ResponseStats(),args=vars(args));(HERE/(args.out+'.receipt.json')).write_text(json.dumps(receipt,indent=2));print(receipt,flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('stage');p.add_argument('--out',default='route');p.add_argument('--horizon',type=int,default=43);p.add_argument('--bhops',type=int,default=3);p.add_argument('--dhops',type=int,default=2);p.add_argument('--workers',type=int,default=4);p.add_argument('--seconds',type=int,default=180);p.add_argument('--seed',type=int,default=0);p.add_argument('--fixed',action='store_true');solve(p.parse_args())
