"""Prepare A plusL with phase hooks protected by its native logical-X readout.

A phase fault is allowed only if independently decoder-correctable or if it
flips X{7,8,9}, measured by the later two-CNOT A readout. Thus the guard does
not rely on a potentially false terminal B syndrome to protect A hooks.
This is a resource contract; the full physical decoder is priced separately.
"""
import argparse,json,os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
from ortools.sat.python import cp_model
from partial_contract import HERE
A=[7,14,13,9,8,21,15];HERALD={7,8,9}

def solve(R=45,early=(7,8),seconds=120,seed=1,cap=None,no8=True,helpers=(0,1)):
    cells=sorted(A+list(helpers));rank=4+len(helpers)
    base=json.loads((HERE.parent/'NATIVE2_20261027/prefix_release.json').read_text())
    release={int(q):t for q,t in base['release'].items()}
    sts={r['q']:r for r in json.loads((HERE.parent/'NATIVE2_20261027/prefix_product_states.json').read_text())['cells']}
    t0=min(release[q] for q in cells);depth=R-t0
    target={q:sum(((g>>i)&1)<<j for j,g in enumerate([85,102,120,7])) for i,q in enumerate(A)}
    edges=[(a,b) for a in cells for b in cells if abs(a//6-b//6)+abs(a%6-b%6)==1]
    m=cp_model.CpModel();cx=[{e:m.NewBoolVar(f'c{t}_{e}') for e in edges} for t in range(depth)]
    used=[{q:m.NewBoolVar(f'u{t}_{q}') for q in cells} for t in range(depth)]
    for t in range(depth):
        for q in cells:
            terms=[v for e,v in cx[t].items() if q in e];m.AddAtMostOne(terms);m.AddMaxEquality(used[t][q],terms)
            if t+t0<release[q] or ((q in early or q in helpers) and t+t0>=R-1):m.Add(used[t][q]==0)
    state=[{q:[m.NewBoolVar(f'x{t}_{q}_{k}') for k in range(rank)] for q in cells} for t in range(depth+1)]
    sig=[{q:[m.NewBoolVar(f's{t}_{q}_{k}') for k in range(5)] for q in cells} for t in range(depth+1)]
    piv={q:m.NewBoolVar(f'p{q}') for q in cells}
    for q in cells:
        m.AddMaxEquality(piv[q],state[0][q])
        for k,v in enumerate(state[-1][q]):
            if q in A and k<4:m.Add(v==(target[q]>>k&1))
            elif q in helpers:m.Add(v==int(k==4+list(helpers).index(q)))
        end=((A.index(q)+1)|8|(16 if q in HERALD else 0)) if q in A else 0
        for k,v in enumerate(sig[-1][q]):m.Add(v==(end>>k&1))
        at=release[q]-t0
        if at<depth:m.Add(piv[q]==int(sts[q]['product_axis']=='X')).OnlyEnforceIf(used[at][q])
    m.Add(sum(piv.values())==rank)
    def xr(z,a,b,on):
        aux=m.NewBoolVar('');m.Add(z+a+b==2*aux).OnlyEnforceIf(on)
    def safe(s,on):
        syn,parity,flag=s[:3],s[3],s[4]
        m.AddBoolOr(syn+[flag,parity.Not(),on.Not()])
        for b in syn:m.AddBoolOr([flag,b.Not(),parity,on.Not()])
        if no8:m.AddBoolOr(syn+[parity.Not(),on.Not()])
    for t in range(depth):
        for q in cells:
            incoming=[e for e in edges if e[1]==q]
            on=m.NewBoolVar('');m.AddMaxEquality(on,[cx[t][e] for e in incoming])
            for arr in (state,sig):
                for k in range(len(arr[t][q])):
                    m.Add(arr[t][q][k]==arr[t+1][q][k]).OnlyEnforceIf(on.Not())
                    for a,b in incoming:xr(arr[t][q][k],arr[t+1][q][k],arr[t+1][a][k],cx[t][a,b])
            alive=m.NewBoolVar('');m.AddMaxEquality(alive,[used[s][q] for s in range(t+1)]);safe(sig[t][q],alive)
        for a,b in edges:
            pair=[m.NewBoolVar('') for _ in range(5)]
            for k,v in enumerate(pair):xr(v,sig[t+1][a][k],sig[t+1][b][k],cx[t][a,b])
            safe(pair,cx[t][a,b])
    ncx=sum(v for layer in cx for v in layer.values())
    if cap is not None:m.Add(ncx<=cap)
    m.Minimize(ncx)
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=seconds;solver.parameters.num_search_workers=1;solver.parameters.random_seed=seed
    status=solver.Solve(m);out=dict(status=solver.StatusName(status),R=R,t0=t0,seconds=solver.WallTime(),A=A,helpers=list(helpers),early_cells=list(early),prefix_stem=base['stem'],direct_plus=True,
        logical_x_herald=sorted(HERALD),exclude_logical_hooks=no8,scope='A conditional plusL; MZ helpers produce known A-X byproducts; logical-X-herald phase hook guard and no8.')
    if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):
        layers=[[list(e) for e,v in layer.items() if solver.Value(v)] for layer in cx]
        initial={q:sum(solver.Value(v)<<k for k,v in enumerate(state[0][q])) for q in cells};rr=initial.copy()
        for layer in layers:
            for a,b in layer:rr[b]^=rr[a]
        assert all((rr[q]&15)==target[q] for q in A)
        assert all(rr[q]==1<<(4+i) for i,q in enumerate(helpers))
        back={q:((A.index(q)+1)|8|(16 if q in HERALD else 0)) if q in A else 0 for q in cells};bad=[]
        def ok(v):return (not no8 or (v&15)!=8) and (bool(v&16) or (v&15)==0 or 9<=(v&15)<=15)
        for t in range(depth-1,-1,-1):
            for a,b in layers[t]:
                if not ok(back[a]^back[b]):bad.append((t,a,b,back[a]^back[b]))
            for a,b in layers[t]:back[b]^=back[a]
            for q in cells:
                if any(any(q in e for e in layer) for layer in layers[:t+1]) and not ok(back[q]):bad.append((t,q,back[q]))
        assert not bad,bad
        operations=[];reuse=[]
        for q in cells:
            first=min((t+t0 for t,layer in enumerate(layers) if any(q in e for e in layer)),default=R-1)
            plus=bool(initial[q]);known=sts[q]['product_axis']==('X' if plus else 'Z')
            if first==release[q] and known:reuse.append(q)
            else:operations.append(dict(time=first-1,kind='RX' if plus else 'R',qs=[q]))
        operations.extend(dict(time=t+t0,kind='CX',qs=e) for t,layer in enumerate(layers) for e in layer)
        operations.extend(dict(time=R-1,kind='M',qs=[q],zero_flag=False) for q in helpers)
        out.update(cx=solver.Value(ncx),ops=layers,initial_rows=initial,operations=sorted(operations,key=lambda o:(o['time'],o['kind'],o['qs'])),reused_inputs=reuse,
             a_ready=R,plus_inputs=[q for q in cells if initial[q]],helper_x_byproducts=[dict(helper=q,targets=[a for a in A if rr[a]>>(4+i)&1]) for i,q in enumerate(helpers)],source_x_byproducts=[],independent_phase_audit=True,final_rows=rr,
             actual_ready={q:max(o['time']+1 for o in operations if q in o['qs']) for q in cells})
    name=f'a_projective_R{R}_h'+('_'.join(map(str,helpers)))
    (HERE/'sol'/f'{name}.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--round',type=int,default=45);ap.add_argument('--seconds',type=float,default=120);ap.add_argument('--early',default='7,8');ap.add_argument('--cap',type=int);ap.add_argument('--no8',action='store_true');ap.add_argument('--helpers',default='0,1')
    a=ap.parse_args();solve(a.round,tuple(map(int,a.early.split(','))) if a.early else (),a.seconds,cap=a.cap,no8=True,helpers=tuple(map(int,a.helpers.split(','))))
