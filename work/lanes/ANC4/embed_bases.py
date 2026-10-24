import os,sys,json,collections,time
sys.dont_write_bytecode=True
from pathlib import Path
from ortools.sat.python import cp_model
import itertools
HERE=Path(__file__).resolve().parent
bases=json.loads((HERE/"parity_bases.json").read_text());classes={}
for b in bases:
 cols=[sum((i in row)<<j for j,row in enumerate(b["rows"])) for i in range(7)]
 key=min(tuple(sorted(sum(((x>>p[j])&1)<<j for j in range(4)) for x in cols)) for p in itertools.permutations(range(4)))
 if key in classes:classes[key]["count"]+=1
 else:classes[key]=dict(basis=b,count=1,edges=[(i,7+j) for j,row in enumerate(b["rows"]) for i in row])
ed=[(q,u) for q in range(36) for u in range(36) if abs(q//6-u//6)+abs(q%6-u%6)==1]
out=[]
for cls in classes.values():
 m=cp_model.CpModel();p=[m.NewIntVar(0,35,'') for i in range(11)];m.AddAllDifferent(p)
 for u,v in cls['edges']:m.AddAllowedAssignments([p[u],p[v]],ed)
 s=cp_model.CpSolver();s.parameters.num_workers=1;s.parameters.max_time_in_seconds=20;st=s.Solve(m)
 v=dict(basis=cls['basis'],count=cls['count'],status=s.StatusName(st),seconds=s.WallTime())
 if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):v['cells']=[s.Value(x) for x in p]
 out.append(v);print(v,flush=True)
(HERE/'direct_basis_embeddings.json').write_text(json.dumps(out,indent=2)+'\n')
