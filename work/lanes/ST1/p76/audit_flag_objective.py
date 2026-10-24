from context76 import *
from flag_objective import build
import argparse
p=argparse.ArgumentParser();p.add_argument('stem');a=p.parse_args();c=json.loads(Path(a.stem).with_suffix('.plan.json').read_text());r=c['meta']['A_resynthesis'];A=c['meta']['A'];R=c['meta']['R'];ops=[tuple(z)for z in r['encoder']];pv=set(r['plus']);flag=r['profile']['flag_code_support'];m=cp_model.CpModel();times=list(range(min(t for t,u,v in ops),max(t for t,u,v in ops)+1));edges=[(i,j)for i,q in enumerate(A)for j,h in enumerate(A)if abs(q//6-h//6)+abs(q%6-h%6)==1];G={(t,i,j):m.NewBoolVar(f'g{t}_{i}_{j}')for t in times for i,j in edges};piv=[m.NewBoolVar('p'+str(i))for i in range(7)]
for(t,i,j),v in G.items():m.Add(v==int((t,A[i],A[j])in ops))
for i,v in enumerate(piv):m.Add(v==int(A[i]in pv))
cost=build(m,G,times,edges,A,piv,flag);assert not m.Validate(),m.Validate();s=cp_model.CpSolver();s.parameters.num_workers=1;st=s.Solve(m);assert st==cp_model.OPTIMAL,s.StatusName(st);profile,_=phase_profile(ops,pv,A,flag);assert s.Value(cost)==profile['blind'],(s.Value(cost),profile)
receipt=dict(stem=a.stem,cp=s.Value(cost),direct=profile,solver=s.StatusName(st));(OUT/'flag_cost_audit.json').write_text(json.dumps(receipt,indent=2));print(json.dumps(receipt))
