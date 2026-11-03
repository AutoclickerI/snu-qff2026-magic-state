"""A phase verification with native flag closures after the D->A layer.

All unflagged phase faults (single-axis and the same-axis pair on every CX)
are required to be decoder-correctable without relying on the terminal B
readout. Helpers finish as product states and are read in the error-detecting
basis. These are state/fault witnesses, not full-noise winner claims.
"""
import argparse,json,os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
from ortools.sat.python import cp_model
from partial_contract import HERE
A=[7,14,13,9,8,21,15]

def solve(R=46,seconds=90,direct=True,helpers=(0,1),seed=1):
    assert direct
    base=json.loads((HERE.parent/'NATIVE2_20261027/prefix_release.json').read_text())
    release={int(q):t for q,t in base['release'].items()}
    sts={r['q']:r for r in json.loads((HERE.parent/'NATIVE2_20261027/prefix_product_states.json').read_text())['cells']}
    cells=sorted(A+list(helpers));t0=min(release[q] for q in cells);depth=R+3-t0
    rankA=4 if direct else 3;rank=rankA+(len(helpers) if direct else 0)
    target={q:sum(((g>>i)&1)<<j for j,g in enumerate([85,102,120]+([7] if direct else []))) for i,q in enumerate(A)}
    target.update({q:(1<<(rankA+i) if direct else 0) for i,q in enumerate(helpers)})
    edges=[(a,b) for a in cells for b in cells if abs(a//6-b//6)+abs(a%6-b%6)==1]
    m=cp_model.CpModel();cx=[{e:m.NewBoolVar(f'c{t}_{e}') for e in edges} for t in range(depth)]
    used=[{q:m.NewBoolVar(f'u{t}_{q}') for q in cells} for t in range(depth)]
    for t in range(depth):
        for q in cells:
            terms=[v for e,v in cx[t].items() if q in e];m.AddAtMostOne(terms);m.AddMaxEquality(used[t][q],terms)
            if t+t0<release[q] or t==depth-1 or (t+t0==R and q in A):m.Add(used[t][q]==0)
        if t+t0>R:
            for (a,b),v in cx[t].items():
                if a in A:m.Add(v==0)  # Only flag->A closures commute with D->A.
    state=[{q:[m.NewBoolVar(f'x{t}_{q}_{k}') for k in range(rank)] for q in cells} for t in range(depth+1)]
    width=4+len(helpers);sig=[{q:[m.NewBoolVar(f's{t}_{q}_{k}') for k in range(width)] for q in cells} for t in range(depth+1)]
    piv={q:m.NewBoolVar(f'p{q}') for q in cells}
    for q in cells:
        m.AddMaxEquality(piv[q],state[0][q])
        for k,v in enumerate(state[-1][q]):m.Add(v==(target[q]>>k&1))
        end=0 if q in A else 1<<(4+list(helpers).index(q))
        for k,v in enumerate(sig[-1][q]):m.Add(v==(end>>k&1))
        at=release[q]-t0
        if at<depth:m.Add(piv[q]==int(sts[q]['product_axis']=='X')).OnlyEnforceIf(used[at][q])
    m.Add(sum(piv.values())==rank)
    def xr(z,a,b,on):
        aux=m.NewBoolVar('');m.Add(z+a+b==2*aux).OnlyEnforceIf(on)
    def safe(s,on):
        syn,parity,flags=s[:3],s[3],s[4:]
        m.AddBoolOr(flags+syn+[parity.Not(),on.Not()])
        for b in syn:m.AddBoolOr(flags+[b.Not(),parity,on.Not()])
    for t in range(depth):
        for q in cells:
            for arr,es,peer in [(state,[e for e in edges if e[1]==q],0),(sig,[e for e in edges if e[1 if direct else 0]==q],0 if direct else 1)]:
                on=m.NewBoolVar('');m.AddMaxEquality(on,[cx[t][e] for e in es])
                if arr is sig and t+t0==R and q in A:
                    injection=(A.index(q)+1)|8
                    for k in range(width):
                        if injection>>k&1:m.Add(sig[t][q][k]+sig[t+1][q][k]==1)
                        else:m.Add(sig[t][q][k]==sig[t+1][q][k])
                    continue
                for k in range(len(arr[t][q])):
                    m.Add(arr[t][q][k]==arr[t+1][q][k]).OnlyEnforceIf(on.Not())
                    for e in es:xr(arr[t][q][k],arr[t+1][q][k],arr[t+1][e[peer]][k],cx[t][e])
            # Before first use, an explicit later reset discards source noise.
            alive=m.NewBoolVar('');m.AddMaxEquality(alive,[used[s][q] for s in range(t+1)])
            safe(sig[t][q],alive)
        for a,b in edges:
            pair=[m.NewBoolVar('') for _ in range(width)]
            for k,v in enumerate(pair):xr(v,sig[t+1][a][k],sig[t+1][b][k],cx[t][a,b])
            safe(pair,cx[t][a,b])
    for q in cells:safe(sig[-1][q],m.NewConstant(1))
    ncx=sum(v for layer in cx for v in layer.values());m.Minimize(ncx)
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=seconds;solver.parameters.num_search_workers=1;solver.parameters.random_seed=seed
    status=solver.Solve(m);out=dict(status=solver.StatusName(status),R=R,t0=t0,seconds=solver.WallTime(),A=A,helpers=list(helpers),prefix_stem=base['stem'],direct_plus=direct,
        scope='A phase-flag closures interleaved after D->A; all prep-phase faults correctable or locally flagged.',terminal_start=R,allow_interleaving=True)
    if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):
        layers=[[list(e) for e,v in layer.items() if solver.Value(v)] for layer in cx]
        initial={q:sum(solver.Value(v)<<k for k,v in enumerate(state[0][q])) for q in cells}
        rr=initial.copy()
        for layer in layers:
            for a,b in layer:rr[b]^=rr[a]
        assert rr==target
        # Independent numeric replay of all constrained phase signatures.
        back={q:(0 if q in A else 1<<(4+list(helpers).index(q))) for q in cells}
        bad=[]
        def check(v):return bool(v>>4) or (v&15)==0 or (9<=v&15<=15)
        for t in range(depth-1,-1,-1):
            for a,b in layers[t]:
                if not check(back[a]^back[b]):bad.append((t,a,b,back[a]^back[b]))
            for a,b in layers[t]:
                if direct:back[b]^=back[a]
                else:back[a]^=back[b]
            if t+t0==R:
                for q in A:back[q]^=(A.index(q)+1)|8
            for q in cells:
                if any(any(q in e for e in layer) for layer in layers[:t+1]) and not check(back[q]):bad.append((t,q,back[q]))
        assert not bad,bad
        operations=[];reuse=[]
        for q in cells:
            first=min((t+t0 for t,layer in enumerate(layers) if any(q in e for e in layer)),default=R+2)
            plus=bool(initial[q]);known=sts[q]['product_axis']==('X' if plus else 'Z')
            if first==release[q] and known:reuse.append(q)
            else:operations.append(dict(time=first-1,kind='RX' if plus else 'R',qs=[q]))
        operations.extend(dict(time=t+t0,kind='CX',qs=e) for t,layer in enumerate(layers) for e in layer)
        if not direct:operations.extend(dict(time=R-1,kind='H',qs=[q]) for q in A)
        operations.extend(dict(time=R+2,kind='MX' if direct else 'M',qs=[q],zero_flag=True) for q in helpers)
        out.update(cx=solver.Value(ncx),ops=layers,initial_rows=initial,operations=sorted(operations,key=lambda o:(o['time'],o['kind'],o['qs'])),reused_inputs=reuse,a_ready=R,
             plus_inputs=[q for q in cells if initial[q]],helper_x_byproducts=[],source_x_byproducts=[],independent_phase_audit=True)
    stem=HERE/'sol'/f'a_overlap_R{R}_h{"_".join(map(str,helpers))}'
    stem.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--round',type=int,default=46);ap.add_argument('--seconds',type=float,default=90);ap.add_argument('--direct',action='store_true');ap.add_argument('--helpers',default='0,1')
    a=ap.parse_args();solve(a.round,a.seconds,True,tuple(map(int,a.helpers.split(','))))
