"""BCX-style joint CSS synthesis with X and Z decoder-safe single-fault contracts."""
import sys,json,time
from ortools.sat.python import cp_model
from build_rounds import H,GENS
from route_grid import nb
import build_suffix as S
from synthesize_grid import build,paths,bridge
import itertools

def solve(T0=30,R=58,seconds=180,workers=2):
    lay=json.loads((H/'layout_joint.json').read_text());D,A,B,C=[lay[k] for k in ('D','A','B','C')]
    cells=[q for q in range(36) if q not in D];helpers=[q for q in cells if q not in A+B+C]
    graph={q:[b for b in cells if nb(q,b)] for q in cells};edges=[(a,b) for a in cells for b in graph[a]]
    logical=[s for s in itertools.combinations(range(7),3) if all(len(set(s)&g)%2==0 for g in GENS)]
    _,flag,support,checks=min((sum(len(bridge(paths(graph,B[i])[f])) for i in s),f,s,[bridge(paths(graph,B[i])[f]) for i in s]) for f in helpers for s in logical)
    rows=[{b[i] for i in row} for b,gs in [(A,GENS+[{0,1,2}]),(B,GENS),(C,GENS+[{0,1,2}])] for row in gs]
    rel=S.release.copy();rel[22]=47
    depth=R-T0;m=cp_model.CpModel()
    sel=[{e:m.NewBoolVar('') for e in edges} for _ in range(depth)]
    used=[];alive=[]
    for t in range(depth):
        used.append({})
        for q in cells:
            inc=[v for e,v in sel[t].items() if q in e];m.AddAtMostOne(inc)
            u=m.NewBoolVar('');m.AddMaxEquality(u,inc);used[t][q]=u
            if t+T0<=rel[q]:m.Add(u==0)
    for t in range(depth+1):
        alive.append({})
        for q in cells:
            a=m.NewBoolVar('');m.AddMaxEquality(a,[used[j][q] for j in range(min(t+1,depth))]);alive[t][q]=a
    def variables(n):return [{q:[m.NewBoolVar('') for _ in range(n)] for q in cells} for _ in range(depth+1)]
    x=variables(11);hx=variables(8+len(helpers));hz=variables(11)
    def col(i):return [int(i in g) for g in GENS]
    for q in cells:
        for j,row in enumerate(rows):m.Add(x[-1][q][j]==int(q in row))
        sx=[0]*4;dx=[0]*(4+len(helpers));sz=[0]*4;dz=[0]*7
        if q in A+B+C:
            block=A if q in A else B if q in B else C;i=block.index(q);v=col(i)
            dx[:3]=v
            if q in B:sx=v+[1];dx[3]=int(i in support)
            dz[:3]=v
            if q in A+C:dz[3:]=v+[1]
            if q in A:sz=v+[1]
        else:dx[4+helpers.index(q)]=1
        for j,v in enumerate(sx+dx):m.Add(hx[-1][q][j]==v)
        for j,v in enumerate(sz+dz):m.Add(hz[-1][q][j]==v)
    def xor(z,a,b,lit):
        k=m.NewIntVar(0,1,'');m.Add(z+a+b==2*k).OnlyEnforceIf(lit);m.Add(k==0).OnlyEnforceIf(lit.Not())
    for t in range(depth):
        for q in cells:
            ins=[e for e in edges if e[1]==q];outs=[e for e in edges if e[0]==q]
            for arr,es,other in [(x,ins,0),(hx,outs,1),(hz,ins,0)]:
                on=m.NewBoolVar('');m.AddMaxEquality(on,[sel[t][e] for e in es])
                for j in range(len(arr[t][q])):
                    m.Add(arr[t][q][j]==arr[t+1][q][j]).OnlyEnforceIf(on.Not())
                    for e in es:xor(arr[t][q][j],arr[t+1][q][j],arr[t+1][e[other]][j],sel[t][e])
    nz={q:m.NewBoolVar('') for q in cells}
    for q in cells:m.AddMaxEquality(nz[q],x[0][q])
    m.Add(sum(nz.values())==11)
    def safe(sig,lit):
        s=sig[:4];d=sig[4:]
        m.AddBoolOr(d+[lit.Not(),s[3].Not(),*s[:3]])
        for b in s[:3]:m.AddBoolOr(d+[lit.Not(),b.Not(),s[3]])
    for t in range(depth+1):
        for q in cells:
            safe(hx[t][q],alive[t][q]);safe(hz[t][q],alive[t][q])
    for t in range(depth):
        for a,b in edges:
            if a>b:continue
            on=m.NewBoolVar('');m.AddMaxEquality(on,[sel[t][a,b],sel[t][b,a]])
            for arr in (hx,hz):
                sig=[]
                for j in range(len(arr[t+1][a])):
                    z=m.NewBoolVar('');xor(z,arr[t+1][a][j],arr[t+1][b][j],on);m.Add(z==0).OnlyEnforceIf(on.Not());sig.append(z)
                safe(sig,on)
    m.Minimize(10*sum(v for ss in sel for v in ss.values())+sum(v for aa in alive for v in aa.values()))
    solver=cp_model.CpSolver();solver.parameters.num_search_workers=workers;solver.parameters.max_time_in_seconds=seconds
    st=solver.Solve(m);out=dict(status=solver.StatusName(st),T0=T0,R=R,seconds=solver.WallTime(),contract='decoder-safe X and Z faults, single-cell and CX-pair support, helper Z flags and pre-round B logical-Z')
    if st in (cp_model.FEASIBLE,cp_model.OPTIMAL):
        ops=[(a,b) for ss in sel for (a,b),v in ss.items() if solver.Value(v)]
        res=dict(seed=R,pivots=[q for q in cells if solver.Value(nz[q])],ops=ops,flag=flag,support=support,checks=checks,prep_cx=len(ops))
        out['resource']=res;out['build']=build(res,tag='cp')
    (H/f'cp_prep_{R}.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)

if __name__=='__main__':solve(R=int(sys.argv[1]) if len(sys.argv)>1 else 58)
