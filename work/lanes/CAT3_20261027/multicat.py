"""Three/four Bell-cat checks with all interactions edge-colored into four ticks.

Every reset, interaction, read, and data wait is retained in the noise model.
This is an abstract diagnostic until every edge has a native implementation.
"""
import collections,concurrent.futures,contextlib,io,json,random,time
import smallcat as s

def color(rounds,seed):
    rng=random.Random(seed);nc=len(rounds[0]);left=len(rounds)*nc;n=max(left,7)
    real=[[0]*n for _ in range(n)]
    for r,groups in enumerate(rounds):
        for c,g in enumerate(groups):
            for d in g:real[r*nc+c][d]+=1
    degree=max(max(map(sum,real)),max(map(sum,zip(*real))))
    m=[row[:] for row in real]
    rows=[degree-sum(row)for row in m];cols=[degree-sum(col)for col in zip(*m)]
    for a in range(n):
        while rows[a]:
            b=rng.choice([b for b in range(n)if cols[b]])
            k=min(rows[a],cols[b]);m[a][b]+=k;rows[a]-=k;cols[b]-=k
    answer=[]
    for tick in range(degree):
        owner={}
        def aug(a,seen):
            choices=[b for b in range(n)if m[a][b]and b not in seen];rng.shuffle(choices)
            for b in choices:
                seen.add(b)
                if b not in owner or aug(owner[b],seen):owner[b]=a;return True
            return False
        ls=list(range(n));rng.shuffle(ls)
        for a in ls:assert aug(a,set())
        layer=[]
        for b,a in owner.items():
            m[a][b]-=1
            if real[a][b]:
                real[a][b]-=1;layer.append((a//nc,a%nc,b))
        answer.append(sorted(layer))
    assert not any(any(row)for row in real)
    return answer

def run(job):
    reps,kind,seed,herald=job
    triples=[[0,1,3],[0,2,4],[0,3,6],[1,2,3]]
    rounds=[s.GROUPS[2]if kind=='same'else [triples[r],sorted(set(range(7))-set(triples[r]))]for r in range(reps)]
    layers=color(rounds,seed)
    name=f'bell{reps}_{kind}_s{seed:03d}_h{int(herald)}'
    stem,out=s.build(ncat=2,herald=herald,staggered=herald,interleaved=True,round_groups=rounds,coupling_layers=layers,name=name)
    assert out['raw']['ok'],(name,out['raw'])
    s.f.DATA=out['data_qubits'];ops,dets=s.f.parse_current(stem.with_suffix('.qasm').read_text())
    out['singles']=s.record_contract.singles(s.f.make_model(ops,dets))
    if out['singles']['c1']<1e-10:
        with contextlib.redirect_stdout(io.StringIO()):p=s.pairs.audit(stem)
        out['c2']=p['c2']
    out['completed']=True;out['edge_colors']=layers
    stem.with_suffix('.result.json').write_text(json.dumps(out,indent=2)+'\n')
    return dict(name=name,reps=reps,kind=kind,seed=seed,herald=herald,c1=out['singles']['c1'],c2=out.get('c2'),cx=out['cx'],ticks=out['ticks'])

if __name__=='__main__':
    jobs=[(reps,kind,seed,False)for reps in (2,3,4)for kind in ('same','mixed')for seed in range(12)]
    rows=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=2)as ex:
        for row in ex.map(run,jobs):
            rows.append(row)
            if len(rows)%12==0:print(json.dumps(dict(done=len(rows),total=len(jobs),best=min((r for r in rows if r['c2']is not None),key=lambda r:r['c2']))),flush=True)
    rows.sort(key=lambda r:r['c2']if r['c2']is not None else float('inf'))
    selected=[]
    for reps in (2,3,4):
        selected.append(next(r for r in rows if r['reps']==reps and r['c2']is not None))
    selected.append(next(r for r in rows if r not in selected and r['c2']is not None))
    for row in selected:
        result=s.exact(s.HERE/'cand'/row['name']);row.update(loss=result['loss'],acceptance=result['acceptance'])
        print(json.dumps(dict(exact=row)),flush=True)
    (s.HERE/'multicat.json').write_text(json.dumps(dict(completed=True,jobs=len(jobs),selected=selected,rows=rows),indent=2)+'\n')
