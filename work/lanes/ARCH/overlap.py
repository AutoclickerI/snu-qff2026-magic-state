"""CP-SAT overlap of flagged Z checks with the actual last prefix steps."""
import itertools
import json
import re
from ortools.sat.python import cp_model
from build import *
W4=[]
for mask in range(1,8):
    s=set()
    for k,g in enumerate(GENS):
        if mask>>k&1:s^=set(g)
    W4.append(sorted(s))
triples=[t for t in itertools.combinations(range(7),3) if (t[0]+1)^(t[1]+1)^(t[2]+1)]

def solve(ts,seed=0):
    c=Circuit();occupied={(t,q) for t,s,r in c.ops if not s.startswith('h ') for q in map(int,re.findall(r'q\[(\d+)\]',s))}
    m=cp_model.CpModel(); times={}; ordered={}
    for k,j in enumerate(ts):
        vs=[m.NewIntVar(27,33,f'ord{k}_{i}') for i in range(6)]
        for u,v in zip(vs,vs[1:]):m.Add(u<v)
        ordered[k]=vs
        for q in W4[j]:
            allowed=[t for t in range(27,34) if (t,D[q]) not in occupied]
            if not allowed:return None
            v=m.NewIntVarFromDomain(cp_model.Domain.FromValues(allowed),f'd{k}_{q}');times[k,q]=v
            flags=[]
            for i in (0,2,3,5):
                b=m.NewBoolVar('');m.Add(v==vs[i]).OnlyEnforceIf(b);flags.append(b)
            m.AddExactlyOne(flags)
        m.AddAllDifferent([times[k,q] for q in W4[j]])
    for q in range(7):
        qs=[v for (k,d),v in times.items() if d==q]
        if qs:m.AddAllDifferent(qs)
    m.Maximize(sum(times.values()))
    solver=cp_model.CpSolver();solver.parameters.num_workers=1;solver.parameters.random_seed=seed
    status=solver.Solve(m)
    if status not in (cp_model.OPTIMAL,cp_model.FEASIBLE):return None
    c.prep(B,False,32);c.prep(C,False,32)
    for i in range(7):c.cx(33,B[i],C[i]);c.cx(34,B[i],D[i])
    c.readblock(34,C,'Z',True);c.readblock(35,B,'X')
    sched=[]
    for k,j in enumerate(ts):
        v=[solver.Value(t) for t in ordered[k]];s,f=A[k],A[k+3]
        c.add(v[0]-1,f'reset q[{s}];','prep');c.add(v[1]-1,f'reset q[{f}];','prep');c.add(v[1]-1,f'h q[{f}];','prep')
        ds=[]
        for q in W4[j]:
            t=solver.Value(times[k,q]); c.cx(t,D[q],s);ds.append([q,t])
        for t in (v[1],v[4]):c.cx(t,f,s)
        b=c.read(v[5]+1,s);flag=c.read(v[4]+1,f,'X');c.dets.extend([f'c[{b}]',f'c[{flag}]'])
        sched.append(dict(support=W4[j],data_steps=ds,flag_steps=[v[1],v[4]]))
    return c.save('overlap'+''.join(map(str,ts)),dict(solver=solver.StatusName(status),schedule=sched,first_round_step=min(t for _,t in [p for s in sched for p in s['data_steps']])))

if __name__=='__main__':
    rows=[];fail=[]
    for ts in triples:
        row=solve(ts)
        if row:rows.append(row)
        else:fail.append(ts)
    (HERE/'overlap_manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
    (HERE/'overlap_infeasible.json').write_text(json.dumps(fail)+'\n')
    print('feasible',len(rows),'infeasible',len(fail))
