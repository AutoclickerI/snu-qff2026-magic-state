"""Exact native old-footprint A-only CSS encoder with logical-X hook exclusion.

A is prepared as zeroL, then H on all seven yields plusL. With the no-C
terminal, every A-X preparation fault becomes Z on output and is detected
by the later B check unless its Steane class is logical Z (class8). Thus
class8 is excluded for all one- and two-endpoint X components. All Z
components affect only A records, so cannot cancel those B detector flips.
A full native noiseless/noisy audit is still required after assembly.
"""
import argparse,json,os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
from pathlib import Path
from ortools.sat.python import cp_model
from partial_contract import HERE
A=[7,14,13,9,8,21,15]

def solve(R=47,seconds=45,seed=1,direct=False,safety=True,early=()):
    base=json.loads((HERE.parent/'NATIVE2_20261027/prefix_release.json').read_text())
    release={int(q):t for q,t in base['release'].items()}
    sts={r['q']:r for r in json.loads((HERE.parent/'NATIVE2_20261027/prefix_product_states.json').read_text())['cells']}
    t0=min(release[q] for q in A);depth=R-t0
    rank=4 if direct else 3
    target={q:sum(((g>>i)&1)<<j for j,g in enumerate([85,102,120]+([7] if direct else []))) for i,q in enumerate(A)}
    edges=[(a,b) for a in A for b in A if abs(a//6-b//6)+abs(a%6-b%6)==1]
    m=cp_model.CpModel();cx=[{e:m.NewBoolVar(f'c{t}_{e}') for e in edges} for t in range(depth)]
    used=[{q:m.NewBoolVar(f'u{t}_{q}') for q in A} for t in range(depth)]
    for t in range(depth):
        for q in A:
            terms=[v for e,v in cx[t].items() if q in e];m.AddAtMostOne(terms);m.AddMaxEquality(used[t][q],terms)
            if t+t0<release[q] or (t==depth-1 and not direct) or (q in early and t+t0>=R-2):m.Add(used[t][q]==0)
    state=[{q:[m.NewBoolVar(f'x{t}_{q}_{k}') for k in range(rank)] for q in A} for t in range(depth+1)]
    sig=[{q:[m.NewBoolVar(f's{t}_{q}_{k}') for k in range(4)] for q in A} for t in range(depth+1)]
    piv={q:m.NewBoolVar(f'p{q}') for q in A}
    for i,q in enumerate(A):
        m.AddMaxEquality(piv[q],state[0][q])
        for k,v in enumerate(state[-1][q]):m.Add(v==(target[q]>>k&1))
        for k,v in enumerate(sig[-1][q]):m.Add(v==(((i+1)|8)>>k&1))
        if release[q]-t0<depth:
            m.Add(piv[q]==int(sts[q]['product_axis']=='X')).OnlyEnforceIf(used[release[q]-t0][q])
    m.Add(sum(piv.values())==rank)
    def xr(z,a,b,on):
        aux=m.NewBoolVar('');m.Add(z+a+b==2*aux).OnlyEnforceIf(on)
    def safe(s,on):
        if safety:m.AddBoolOr(s[:3]+[s[3].Not(),on.Not()])
    for t in range(depth):
        for q in A:
            for arr,es,peer in [(state,[e for e in edges if e[1]==q],0),(sig,[e for e in edges if e[1 if direct else 0]==q],0 if direct else 1)]:
                on=m.NewBoolVar('');m.AddMaxEquality(on,[cx[t][e] for e in es])
                for k in range(len(arr[t][q])):
                    m.Add(arr[t][q][k]==arr[t+1][q][k]).OnlyEnforceIf(on.Not())
                    for e in es:xr(arr[t][q][k],arr[t+1][q][k],arr[t+1][e[peer]][k],cx[t][e])
            # Idle/reset errors matter only after initialization. Conservative all-time
            # class exclusion is sufficient and cheap for this seven-cell module.
            always=m.NewConstant(1);safe(sig[t][q],always)
        for a,b in edges:
            pair=[m.NewBoolVar('') for _ in range(4)]
            for k,v in enumerate(pair):xr(v,sig[t+1][a][k],sig[t+1][b][k],cx[t][a,b])
            safe(pair,cx[t][a,b])
    ncx=sum(v for layer in cx for v in layer.values());m.Minimize(ncx)
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=seconds;solver.parameters.num_search_workers=1;solver.parameters.random_seed=seed
    status=solver.Solve(m);out=dict(status=solver.StatusName(status),R=R,t0=t0,seconds=solver.WallTime(),A=A,source=base['stem'],scope='Native A-only state and logical-hook contract; complete integration pending.',direct_plus=direct,phase_safety=safety,early_cells=list(early))
    if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):
        layers=[[list(e) for e,v in layer.items() if solver.Value(v)] for layer in cx]
        initial={q:sum(solver.Value(v)<<k for k,v in enumerate(state[0][q])) for q in A}
        rr=initial.copy()
        for layer in layers:
            for a,b in layer:rr[b]^=rr[a]
        assert rr==target
        operations=[];reuse=[]
        for q in A:
            first=min((t+t0 for t,layer in enumerate(layers) if any(q in e for e in layer)),default=R-1)
            plus=bool(initial[q]);known=sts[q]['product_axis']==('X' if plus else 'Z')
            if first==release[q] and known:reuse.append(q)
            else:operations.append(dict(time=first-1,kind='RX' if plus else 'R',qs=[q]))
        operations.extend(dict(time=t+t0,kind='CX',qs=e) for t,layer in enumerate(layers) for e in layer)
        if not direct:operations.extend(dict(time=R-1,kind='H',qs=[q]) for q in A)
        out.update(cx=solver.Value(ncx),ops=layers,initial_rows=initial,operations=sorted(operations,key=lambda o:(o['time'],o['kind'],o['qs'])),reused_inputs=reuse,helpers=[],a_ready=R,plus_inputs=[q for q in A if initial[q]],helper_x_byproducts=[],source_x_byproducts=[])
    (HERE/'sol'/f'a_{"plus" if direct else "only"}_R{R}{"" if safety else "_state"}{"_early"+"_".join(map(str,early)) if early else ""}.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--round',type=int,default=47);ap.add_argument('--seconds',type=float,default=45);ap.add_argument('--direct',action='store_true');ap.add_argument('--no-safety',action='store_true');ap.add_argument('--early',default='');a=ap.parse_args();solve(a.round,a.seconds,direct=a.direct,safety=not a.no_safety,early=tuple(map(int,a.early.split(','))) if a.early else ())
