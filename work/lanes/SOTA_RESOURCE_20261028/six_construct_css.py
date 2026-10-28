"""Construct joint native CSS resources with measured, unconstrained helpers.

The physical output row space is prescribed only on A/B/C. Helper rows may
retain information and are measured in X; final H on A turns its Z byproducts
into harmless A-readout X offsets. Complete circuit evaluation handles noise.
This constructive search supplies witnesses without requiring a global solve.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse, json, random, sys, time
from pathlib import Path
from ortools.sat.python import cp_model
import stim

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'work/lanes/NATIVE2_20261027'),str(ROOT/'work/lanes/END2_20261027')]
import a_factory as af


def canonical(rows, width, keep):
    piv={}
    for j in range(width):
        v=sum(1<<q for q in keep if rows[q]>>j&1)
        while v:
            k=v.bit_length()-1
            if k in piv: v ^= piv[k]
            else: piv[k]=v; break
    for j in sorted(piv):
        for k in sorted(piv):
            if k>j and piv[k]>>j&1: piv[k]^=piv[j]
    return tuple(piv[k] for k in sorted(piv))


def construct(target, width, cells, outputs, rng, basis_mode='mixed'):
    # A local choice of helper labels is a starting witness, not an imposed
    # physical contract. Removing gates below may change every helper label.
    rows=target.copy()
    for q in cells:
        if q not in outputs and rng.random()<.7:
            rows[q]=rng.choice([target[v] for v in af.ADJ[q]]+[0])
    basis=[1<<j for j in range(width)]
    for _ in range(width*2 if basis_mode!='identity' else 0):
        group=rng.choice([range(3),range(3,6),range(6,10)]) if basis_mode=='block' else range(width)
        a,b=rng.sample(list(group),2); basis[b]^=basis[a]
    rows={q:sum(((v&b).bit_count()&1)<<j for j,b in enumerate(basis)) for q,v in rows.items()}
    back=[]; locked=set(); order=list(range(width)); rng.shuffle(order)
    for j in order:
        allowed=set(cells)-locked
        terms=[q for q in allowed if rows[q]>>j&1]
        if not terms: continue
        roots=list(terms); rng.shuffle(roots)
        # Favor boundary pivots so later elimination can still use the grid.
        roots.sort(key=lambda q:sum(v in allowed for v in af.ADJ[q])+rng.random()*2)
        root=roots[0]
        tree=af.tree_for(root,terms,allowed,rng)
        if tree is None: return None
        for u,v in tree:
            if not rows[v]>>j&1:
                rows[v]^=rows[u]; back.append((u,v))
        for u,v in reversed(tree):
            rows[v]^=rows[u]; back.append((u,v))
        assert all(not rows[q]>>j&1 for q in allowed if q!=root)
        locked.add(root)
    if sum(bool(v) for v in rows.values())!=width: return None
    initial=rows.copy(); gates=list(reversed(back))
    desired=canonical(target,width,outputs)
    def evaluate(gs):
        r=initial.copy()
        for a,b in gs: r[b]^=r[a]
        return canonical(r,width,outputs)
    assert evaluate(gates)==desired
    # State/isometry simplification: only the required A/B/C state matters.
    indices=list(range(len(gates))); rng.shuffle(indices)
    for i in indices:
        if i>=len(gates): continue
        trial=gates[:i]+gates[i+1:]
        if evaluate(trial)==desired: gates=trial
    return initial,gates


def schedule(initial,gates,releases,roles,rng,cp_seconds=0):
    used=set(roles['A']+roles['B']+roles['C'])|{q for e in gates for q in e}
    pred=[{j for j,(a,b) in enumerate(gates[:i]) if d==a or b==c}
          for i,(c,d) in enumerate(gates)]
    remaining=set(range(len(gates))); done=set(); times=[None]*len(gates)
    busy={q:releases[q]+1 for q in used}
    while remaining:
        avail=[i for i in remaining if pred[i]<=done]
        def priority(i):
            a,b=gates[i]
            return max(busy[a],busy[b],max((times[j]+1 for j in pred[i]),default=0))+rng.random()*.05
        i=min(avail,key=priority); a,b=gates[i]
        times[i]=max(busy[a],busy[b],max((times[j]+1 for j in pred[i]),default=0))
        busy[a]=busy[b]=times[i]+1; done.add(i); remaining.remove(i)
    if cp_seconds:
        upper=max(times)+1
        m=cp_model.CpModel()
        starts=[m.NewIntVar(max(releases[a],releases[b])+1,upper-1,f's{i}') for i,(a,b) in enumerate(gates)]
        iv=[m.NewFixedSizeIntervalVar(s,1,f'g{i}') for i,s in enumerate(starts)]
        for q in used: m.AddNoOverlap([v for v,e in zip(iv,gates) if q in e])
        for i,ps in enumerate(pred):
            for j in ps: m.Add(starts[i]>=starts[j]+1)
        finish=m.NewIntVar(0,upper+1,'finish')
        for i,e in enumerate(gates): m.Add(finish>=starts[i]+1+int(bool(set(e)&set(roles['A']))))
        m.Minimize(1000*finish-sum(starts))
        for s,t in zip(starts,times): m.AddHint(s,t)
        sol=cp_model.CpSolver();sol.parameters.num_search_workers=1;sol.parameters.max_time_in_seconds=cp_seconds
        status=sol.Solve(m)
        if status in (cp_model.OPTIMAL,cp_model.FEASIBLE): times=[sol.Value(s) for s in starts]
    first={q:min((t for t,e in zip(times,gates) if q in e),default=releases[q]+1) for q in used}
    last={q:max((t for t,e in zip(times,gates) if q in e),default=first[q]-1) for q in used}
    ops=[dict(time=first[q]-1,kind='RX' if initial[q] else 'R',qs=[q]) for q in sorted(used)]
    ops += [dict(time=t,kind='CX',qs=list(e)) for t,e in zip(times,gates)]
    ops += [dict(time=last[q]+1,kind='H',qs=[q]) for q in roles['A']]
    helpers=sorted(used-set(roles['A']+roles['B']+roles['C']))
    ops += [dict(time=last[q]+1,kind='MX',qs=[q],byproduct_record=True) for q in helpers]
    return dict(roles=roles,cx=len(gates),ready=max(o['time']+1 for o in ops),helpers=helpers,
                pivots=initial,operations=sorted(ops,key=lambda o:(o['time'],o['kind'],o['qs'])),
                helper_rule='Arbitrary final CSS rows, measured in X; A is H rotated at final use.',
                initial_rows=initial,ordered_gates=[list(e) for e in gates],
                scope='Native joint CSS module. Full source, record contract and noise must be checked.')


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('source');ap.add_argument('--trials',type=int,default=1000)
    ap.add_argument('--seed',type=int,default=0);ap.add_argument('--name',default='joint_measured')
    ap.add_argument('--basis',choices=['mixed','block','identity'],default='mixed')
    ap.add_argument('--exclude',default='')
    args=ap.parse_args(); started=time.perf_counter()
    source=json.loads(Path(args.source).read_text());roles=source['roles']
    excluded={int(q) for q in args.exclude.split(',') if q}
    assert not excluded & set(roles['A']+roles['B']+roles['C'])
    cells=sorted(set(range(36))-set(roles['D'])-excluded)
    outputs=set(roles['A']+roles['B']+roles['C'])
    generators=[{q for i,q in enumerate(roles['A']) if mask>>i&1} for mask in (85,102,120)]
    generators += [{q for i in range(7) if mask>>i&1 for q in (roles['B'][i],roles['C'][i])} for mask in (85,102,120)]
    generators += [{q for i,q in enumerate(roles['C']) if mask>>i&1} for mask in (7,25,42,64)]
    width=len(generators)
    target={q:sum(1<<j for j,row in enumerate(generators) if q in row) for q in cells}
    af.CELLS=cells;af.ADJ={q:[v for v in cells if abs(q//6-v//6)+abs(q%6-v%6)==1] for q in cells}
    releases={int(q):t for q,t in source['release'].items()}
    rng=random.Random(args.seed); rows=[];seen=set(); successes=0
    folder=HERE/'joint_modules';folder.mkdir(exist_ok=True)
    for trial in range(args.trials):
        result=construct(target,width,cells,outputs,rng,args.basis)
        if result is None:continue
        initial,gates=result
        key=(tuple(sorted(initial.items())),tuple(gates))
        if key in seen:continue
        seen.add(key);successes+=1
        row=schedule(initial,gates,releases,roles,rng)
        row.update(trial=trial,source=args.source,square_mask=source['square_mask'])
        rows.append(row);rows.sort(key=lambda r:(r['ready'],r['cx']))
        rows=rows[:20]
        if row is rows[0]:
            (folder/f'{args.name}_best.json').write_text(json.dumps(row,indent=2)+'\n')
            print(json.dumps(dict(trial=trial,cx=row['cx'],ready=row['ready'],successes=successes,seconds=time.perf_counter()-started)),flush=True)
    for i,row in enumerate(rows[:6]):
        opt=schedule(row['initial_rows'],row['ordered_gates'],releases,roles,rng,cp_seconds=2)
        row.update(opt)
        (folder/f'{args.name}_{i}.json').write_text(json.dumps(row,indent=2)+'\n')
    (folder/f'{args.name}_results.json').write_text(json.dumps(dict(source=args.source,trials=args.trials,successes=successes,seconds=time.perf_counter()-started,candidates=rows),indent=2)+'\n')
    print(json.dumps(dict(completed=True,successes=successes,seconds=time.perf_counter()-started,best=[(r['ready'],r['cx']) for r in rows[:6]])),flush=True)

if __name__=='__main__':main()
