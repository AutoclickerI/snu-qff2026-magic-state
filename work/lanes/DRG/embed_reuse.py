import sys,json,collections,time
from ortools.sat.python import cp_model
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/DR'); import poc
s={int(k):[(t,typ,frozenset(S)) for t,typ,S in v] for k,v in json.load(open('/home/jihoon/competitions/quantumn/work/lanes/DR/sched_zfirst.json')).items()}
N=6; cells=list(range(36)); allowed=[[a,b] for a in cells for b in cells if abs(a//6-b//6)+abs(a%6-b%6)==1]
def solve(name,bfn):
 b,_,_=bfn(s); n=b.next_q; p=[None]*n; ints={}
 for q in range(n):
  ts=[t for t,k,kind,qs,tag in b.ops if q in qs]; ints[q]=(min(ts),max(ts))
 m=cp_model.CpModel(); p=[m.NewIntVar(0,35,f'p{q}') for q in range(n)]
 # data unique
 for a in range(7):
  for c in range(a):m.Add(p[a]!=p[c])
 # overlap noncollision; data intervals encompass all but ensure all
 for a in range(n):
  for c in range(a):
   if not (ints[a][1]<ints[c][0] or ints[c][1]<ints[a][0]):m.Add(p[a]!=p[c])
 # cx adjacency
 E=set(tuple(qs) for t,k,kind,qs,tag in b.ops if kind=='cx')
 for a,c in E:m.AddAllowedAssignments([p[a],p[c]],allowed)
 # use no symmetry; break data by row maybe optional
 print(name,'n',n,'E',len(E),'overlap pairs',sum(1 for a in range(n) for c in range(a) if not(ints[a][1]<ints[c][0] or ints[c][1]<ints[a][0])),flush=True)
 sol=cp_model.CpSolver();sol.parameters.max_time_in_seconds=300;sol.parameters.num_search_workers=8;sol.parameters.log_search_progress=False
 r=sol.Solve(m); print('RESULT',sol.StatusName(r),flush=True)
 if r in (cp_model.FEASIBLE,cp_model.OPTIMAL):
  a=[sol.Value(z) for z in p]; print('MAP',a,[(x//6,x%6) for x in a],flush=True)
  json.dump({'map':a,'intervals':ints,'n':n},open('/home/jihoon/competitions/quantumn/work/lanes/DRG/'+name+'_map.json','w'))
for name,bfn in [('pair',lambda s:poc.build_hybrid(s,z_mode='pair')),('cat1',lambda s:poc.build_hybrid(s,z_mode='cat1')),('clean',lambda s:poc.build_clean(s,clean_z=True))]:solve(name,bfn)
