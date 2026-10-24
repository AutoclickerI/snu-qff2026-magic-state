import os,sys,json,time
sys.dont_write_bytecode=True
from pathlib import Path
from ortools.sat.python import cp_model
HERE=Path(__file__).resolve().parent
from generate import PAR
lay=json.loads((HERE/'grid_layout.json').read_text());B,F=lay['b'],lay['f'];qs=B+F

def run(depth):
 m=cp_model.CpModel();one=m.NewBoolVar('');m.Add(one==1)
 ed=[(i,j) for i in range(11) for j in range(11) if abs(qs[i]//6-qs[j]//6)+abs(qs[i]%6-qs[j]%6)==1]
 s=[{e:m.NewBoolVar('') for e in ed} for t in range(depth)]
 c=[[[m.NewBoolVar('') for bit in range(7)] for q in range(11)] for t in range(depth+1)]
 for q in range(11):
  for bit in range(7):m.Add(c[0][q][bit]==int(q==bit))
 for t in range(depth):
  for q in range(11):
   m.AddAtMostOne([v for e,v in s[t].items() if q in e])
   for bit in range(7):
    inc=[]
    for u,v in ed:
     if v==q:
      z=m.NewBoolVar('');m.AddMultiplicationEquality(z,[s[t][u,v],c[t][u][bit]]);inc.append(z)
    m.AddBoolXOr([c[t+1][q][bit],c[t][q][bit],*inc,one])
 # Exact B output rows; F can be any independent basis of the four parities.
 for q in range(7):
  for bit in range(7):m.Add(c[-1][q][bit]==int(q==bit))
 hs=[sum(1<<i for i in row) for row in PAR];span={0}
 for h in hs:span|={h^v for v in list(span)}
 vals=[]
 for q in range(7,11):
  v=m.NewIntVar(1,127,'');m.Add(v==sum(c[-1][q][bit]*(1<<bit) for bit in range(7)));m.AddAllowedAssignments([v],[(x,) for x in span if x]);vals.append(v)
 # Every independent 4-row basis, any physical row assignment.
 table=[]
 import itertools
 for rows in itertools.permutations(sorted(span-{0}),4):
  ss={0}
  for h in rows:ss|={x^h for x in list(ss)}
  if len(ss)==16:table.append(rows)
 m.AddAllowedAssignments(vals,table)
 m.Minimize(sum(v for sl in s for v in sl.values()))
 sol=cp_model.CpSolver();sol.parameters.num_workers=1;sol.parameters.max_time_in_seconds=180
 st=sol.Solve(m);out=dict(depth=depth,status=sol.StatusName(st),seconds=sol.WallTime(),bound=sol.BestObjectiveBound())
 if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):
  out.update(ops=[[(qs[u],qs[v]) for u,v in ed if sol.Value(s[t][u,v])] for t in range(depth)],B=B,F=F,parities=[[i for i in range(7) if sol.Value(v)>>i&1] for v in vals],cx=int(sol.ObjectiveValue()))
 (HERE/f'grid_checker_d{depth}.json').write_text(json.dumps(out,indent=2)+'\n');print(out,flush=True)
if __name__=='__main__':
 assert os.getloadavg()[0]<os.cpu_count()-2
 run(20)
