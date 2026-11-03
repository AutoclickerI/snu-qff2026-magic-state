"""Native joint dual-A/BC preparation with free MX-measured helper parities.

State-only CP search: complete fault propagation and noisy pricing are mandatory
before treating any returned witness as a competitive circuit.
"""
import argparse,json,os,time
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
from pathlib import Path
from ortools.sat.python import cp_model
from terminal_variants import make_variant,HERE


def solve(name,R=47,mask=29,swap=0,seconds=120,seed=1,cap=None,hint=None):
    pc=make_variant(mask,swap,True,True)
    cells=sorted(pc.COLS);helpers=pc.HELPERS;rank=pc.rank
    boundary=json.loads((HERE.parent/'NATIVE2_20261027/prefix_release.json').read_text())
    release={int(q):int(t) for q,t in boundary['release'].items()}
    states={r['q']:r for r in json.loads((HERE.parent/'NATIVE2_20261027/prefix_product_states.json').read_text())['cells']}
    known={q:s['product_axis'] for q,s in states.items() if not s.get('phase_constant') and not s.get('phase_xor')}
    edges=[(a,b) for a in cells for b in cells if abs(a//6-b//6)+abs(a%6-b%6)==1]
    m=cp_model.CpModel();cx=[];used=[]
    for t in range(R):
        gates={e:m.NewBoolVar(f'g{t}_{e[0]}_{e[1]}') for e in edges};cx.append(gates)
        use={q:m.NewBoolVar(f'u{t}_{q}') for q in cells};used.append(use)
        for q in cells:
            terms=[v for e,v in gates.items() if q in e];m.AddAtMostOne(terms);m.AddMaxEquality(use[q],terms)
            if t<release[q] or(t==release[q] and q not in known):m.Add(use[q]==0)
            if t==R-1 and q in set(helpers+pc.A):m.Add(use[q]==0)
    state=[{q:[m.NewBoolVar(f'x{t}_{q}_{k}') for k in range(rank)] for q in cells} for t in range(R+1)]
    nz={q:m.NewBoolVar(f'p{q}') for q in cells}
    for q in cells:
        m.AddMaxEquality(nz[q],state[0][q])
        if q in pc.CELLS:
            for k,v in enumerate(state[-1][q]):m.Add(v==(pc.COLS[q]>>k&1))
        if q in known and 0<=release[q]<R:m.Add(nz[q]==int(known[q]=='X')).OnlyEnforceIf(used[release[q]][q])
    m.Add(sum(nz.values())==rank)
    for t in range(R):
        for b in cells:
            es=[e for e in edges if e[1]==b];on=m.NewBoolVar('')
            m.AddMaxEquality(on,[cx[t][e] for e in es])
            for k in range(rank):
                m.Add(state[t+1][b][k]==state[t][b][k]).OnlyEnforceIf(on.Not())
                for a,_ in es:
                    aux=m.NewBoolVar('');m.Add(state[t+1][b][k]+state[t][b][k]+state[t][a][k]==2*aux).OnlyEnforceIf(cx[t][a,b])
    ncx=sum(v for layer in cx for v in layer.values())
    if cap is not None:m.Add(ncx<=cap)
    # Favor late first uses and early termination by minimizing occupied lifespan.
    live=[]
    for q in cells:
        for t in range(R):
            before=m.NewBoolVar('');after=m.NewBoolVar('');span=m.NewBoolVar('')
            m.AddMaxEquality(before,[used[s][q] for s in range(t+1)])
            m.AddMaxEquality(after,[used[s][q] for s in range(t,R)])
            m.AddBoolAnd([before,after]).OnlyEnforceIf(span)
            m.AddBoolOr([before.Not(),after.Not(),span]);live.append(span)
    m.Minimize(20*ncx+sum(live))
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=seconds;solver.parameters.num_search_workers=1;solver.parameters.random_seed=seed
    status=solver.Solve(m)
    out=dict(status=solver.StatusName(status),seconds=solver.WallTime(),R=R,square_mask=mask,swap_mask=swap,
      state_only=True,requires_full_noisy_audit=True,rank=rank,cells=cells,helpers=helpers,
      roles=pc.roles,post_h=pc.A,release=release,known_initial=known,source=boundary['stem'])
    if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):
        layers=[[list(e) for e,v in layer.items() if solver.Value(v)] for layer in cx]
        initial={q:sum(solver.Value(v)<<k for k,v in enumerate(state[0][q])) for q in cells}
        final={q:sum(solver.Value(v)<<k for k,v in enumerate(state[-1][q])) for q in cells}
        check=initial.copy()
        for layer in layers:
            for a,b in layer:check[b]^=check[a]
        assert check==final and all(final[q]==pc.COLS[q] for q in pc.CELLS)
        out.update(cx=solver.Value(ncx),ops=layers,pivots=initial,final_rows=final,target_columns=pc.COLS,objective=solver.ObjectiveValue(),bound=solver.BestObjectiveBound())
    (HERE/'sol'/f'{name}.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('name');ap.add_argument('--round',type=int,default=47);ap.add_argument('--mask',type=lambda x:int(x,0),default=29)
    ap.add_argument('--swap',type=lambda x:int(x,0),default=0);ap.add_argument('--seconds',type=float,default=120);ap.add_argument('--seed',type=int,default=1);ap.add_argument('--cap',type=int)
    a=ap.parse_args();solve(a.name,a.round,a.mask,a.swap,a.seconds,a.seed,a.cap)
