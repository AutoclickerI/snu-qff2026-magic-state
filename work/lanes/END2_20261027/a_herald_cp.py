"""Prepare A plusL with phase hooks protected by its native logical-X readout.

A phase fault is allowed only if independently decoder-correctable or if it
flips X{7,8,9}, measured by the later two-CNOT A readout. Thus the guard does
not rely on a potentially false terminal B syndrome to protect A hooks.
This is a resource contract; the full physical decoder is priced separately.
"""
import argparse,json,os
from pathlib import Path
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
from ortools.sat.python import cp_model
from partial_contract import HERE
A=[7,14,13,9,8,21,15];HERALD={7,8,9}

def solve(R=46,early=(7,8),seconds=120,seed=1,cap=None,no8=False,boundary=None,herald=None,soft=False,product_states=None,tag=None,excluded_multisets=()):
    hset=set(herald or HERALD)
    assert hset<=set(A) and len(hset)%2==1
    assert __import__('functools').reduce(lambda a,b:a^b,(A.index(q)+1 for q in hset))==0
    base=json.loads((Path(boundary) if boundary else HERE.parent/'NATIVE2_20261027/prefix_release.json').read_text())
    release={int(q):t for q,t in base['release'].items()}
    state_path=Path(product_states or base.get('product_states') or HERE.parent/'NATIVE2_20261027/prefix_product_states.json')
    sts={r['q']:r for r in json.loads(state_path.read_text())['cells']}
    t0=min(release[q] for q in A);depth=R-t0
    target={q:sum(((g>>i)&1)<<j for j,g in enumerate([85,102,120,7])) for i,q in enumerate(A)}
    edges=[(a,b) for a in A for b in A if abs(a//6-b//6)+abs(a%6-b%6)==1]
    m=cp_model.CpModel();cx=[{e:m.NewBoolVar(f'c{t}_{e}') for e in edges} for t in range(depth)]
    if excluded_multisets:
        counts=[]
        for e in edges:
            count=m.NewIntVar(0,depth,f'edge_count_{e}')
            m.Add(count==sum(layer[e] for layer in cx));counts.append(count)
        rows=[]
        for excluded in excluded_multisets:
            rows.append([sum(tuple(g)==e for layer in excluded for g in layer) for e in edges])
        m.AddForbiddenAssignments(counts,rows)
    used=[{q:m.NewBoolVar(f'u{t}_{q}') for q in A} for t in range(depth)]
    for t in range(depth):
        for q in A:
            terms=[v for e,v in cx[t].items() if q in e];m.AddAtMostOne(terms);m.AddMaxEquality(used[t][q],terms)
            if t+t0<release[q] or (q in early and t+t0>=R-1):m.Add(used[t][q]==0)
    state=[{q:[m.NewBoolVar(f'x{t}_{q}_{k}') for k in range(4)] for q in A} for t in range(depth+1)]
    sig=[{q:[m.NewBoolVar(f's{t}_{q}_{k}') for k in range(5)] for q in A} for t in range(depth+1)]
    piv={q:m.NewBoolVar(f'p{q}') for q in A}
    for q in A:
        m.AddMaxEquality(piv[q],state[0][q])
        for k,v in enumerate(state[-1][q]):m.Add(v==(target[q]>>k&1))
        end=(A.index(q)+1)|8|(16 if q in hset else 0)
        for k,v in enumerate(sig[-1][q]):m.Add(v==(end>>k&1))
        at=release[q]-t0
        if at<depth:m.Add(piv[q]==int(sts[q]['product_axis']=='X')).OnlyEnforceIf(used[at][q])
    m.Add(sum(piv.values())==4)
    def xr(z,a,b,on):
        aux=m.NewBoolVar('');m.Add(z+a+b==2*aux).OnlyEnforceIf(on)
    cost=[]
    def safe(s,on,weight=1):
        syn,parity,flag=s[:3],s[3],s[4]
        bad=m.NewBoolVar('phase_bad') if soft else None
        extra=[bad] if soft else []
        m.AddBoolOr(syn+[flag,parity.Not(),on.Not()]+extra)
        for b in syn:m.AddBoolOr([flag,b.Not(),parity,on.Not()]+extra)
        if no8:m.AddBoolOr(syn+[parity.Not(),on.Not()])
        if soft:cost.append(weight*bad)
    for t in range(depth):
        for q in A:
            incoming=[e for e in edges if e[1]==q]
            on=m.NewBoolVar('');m.AddMaxEquality(on,[cx[t][e] for e in incoming])
            for arr in (state,sig):
                for k in range(len(arr[t][q])):
                    m.Add(arr[t][q][k]==arr[t+1][q][k]).OnlyEnforceIf(on.Not())
                    for a,b in incoming:xr(arr[t][q][k],arr[t+1][q][k],arr[t+1][a][k],cx[t][a,b])
            alive=m.NewBoolVar('');m.AddMaxEquality(alive,[used[s][q] for s in range(t+1)])
            if soft:
                prior=m.NewBoolVar('')
                if t:m.AddMaxEquality(prior,[used[s][q] for s in range(t)])
                else:m.Add(prior==0)
                wait=m.NewBoolVar('');m.AddBoolAnd([prior,used[t][q].Not()]).OnlyEnforceIf(wait);m.AddBoolOr([prior.Not(),used[t][q],wait])
                firstplus=m.NewBoolVar('');m.AddBoolAnd([used[t][q],prior.Not(),piv[q]]).OnlyEnforceIf(firstplus);m.AddBoolOr([used[t][q].Not(),prior,piv[q].Not(),firstplus])
                safe(sig[t][q],wait,10);safe(sig[t+1][q],used[t][q],4);safe(sig[t][q],firstplus,15)
            else:safe(sig[t][q],alive)
        for a,b in edges:
            pair=[m.NewBoolVar('') for _ in range(5)]
            for k,v in enumerate(pair):xr(v,sig[t+1][a][k],sig[t+1][b][k],cx[t][a,b])
            safe(pair,cx[t][a,b],4)
    ncx=sum(v for layer in cx for v in layer.values())
    if cap is not None:m.Add(ncx<=cap)
    m.Minimize(1000*sum(cost)+ncx if soft else ncx)
    solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=seconds;solver.parameters.num_search_workers=1;solver.parameters.random_seed=seed
    status=solver.Solve(m);out=dict(status=solver.StatusName(status),R=R,t0=t0,seconds=solver.WallTime(),A=A,early_cells=list(early),prefix_stem=base['stem'],direct_plus=True,
        logical_x_herald=sorted(hset),exclude_logical_hooks=no8,soft_phase_objective=soft,product_states=str(state_path),excluded_gate_multisets=len(excluded_multisets),scope=('Native A plusL; weighted residual phase-hook proxy minimized. Residual unsafe classes are listed explicitly; this is not a full logical-loss objective.' if soft else 'Native A plusL; each unflagged phase hook independently correctable or flips later logical-X herald.'))
    if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):
        layers=[[list(e) for e,v in layer.items() if solver.Value(v)] for layer in cx]
        initial={q:sum(solver.Value(v)<<k for k,v in enumerate(state[0][q])) for q in A};rr=initial.copy()
        for layer in layers:
            for a,b in layer:rr[b]^=rr[a]
        assert rr==target
        back={q:(A.index(q)+1)|8|(16 if q in hset else 0) for q in A};bad=[]
        def ok(v):return (not no8 or (v&15)!=8) and (bool(v&16) or (v&15)==0 or 9<=(v&15)<=15)
        for t in range(depth-1,-1,-1):
            for a,b in layers[t]:
                if not ok(back[a]^back[b]):bad.append((t,a,b,back[a]^back[b]))
            for a,b in layers[t]:back[b]^=back[a]
            for q in A:
                if any(any(q in e for e in layer) for layer in layers[:t+1]) and not ok(back[q]):bad.append((t,q,back[q]))
        assert soft or not bad,bad
        operations=[];reuse=[]
        for q in A:
            first=min((t+t0 for t,layer in enumerate(layers) if any(q in e for e in layer)),default=R-1)
            plus=bool(initial[q]);known=sts[q]['product_axis']==('X' if plus else 'Z')
            if first==release[q] and known:reuse.append(q)
            else:operations.append(dict(time=first-1,kind='RX' if plus else 'R',qs=[q]))
        operations.extend(dict(time=t+t0,kind='CX',qs=e) for t,layer in enumerate(layers) for e in layer)
        out.update(cx=solver.Value(ncx),ops=layers,initial_rows=initial,operations=sorted(operations,key=lambda o:(o['time'],o['kind'],o['qs'])),reused_inputs=reuse,
             helpers=[],a_ready=R,plus_inputs=[q for q in A if initial[q]],helper_x_byproducts=[],source_x_byproducts=[],independent_phase_audit=not bad,phase_audit_bad=bad,phase_cost=solver.Value(sum(cost)) if soft else 0,
             actual_ready={q:max(o['time']+1 for o in operations if q in o['qs']) for q in A})
    name=f'a_herald_R{R}_early'+('_'.join(map(str,early)) if early else 'none')+('_no8' if no8 else '')+('_earlysource' if boundary else '')+('_hx'+'_'.join(map(str,sorted(hset))) if hset!=HERALD else '')+('_soft' if soft else '')
    if tag:name+='_'+tag
    (HERE/'sol'/f'{name}.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
    return out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--round',type=int,default=46);ap.add_argument('--seconds',type=float,default=120);ap.add_argument('--early',default='7,8');ap.add_argument('--cap',type=int);ap.add_argument('--no8',action='store_true');ap.add_argument('--boundary');ap.add_argument('--herald',default='7,8,9');ap.add_argument('--soft',action='store_true');ap.add_argument('--product-states');ap.add_argument('--tag')
    a=ap.parse_args();solve(a.round,tuple(map(int,a.early.split(','))) if a.early else (),a.seconds,cap=a.cap,no8=a.no8,boundary=a.boundary,herald=tuple(map(int,a.herald.split(','))),soft=a.soft,product_states=a.product_states,tag=a.tag)
