"""Depth-oriented native A resource seeds for the corrected partial-square end.

Both direct |+L> preparation and its three-variable dual are searched.  The
source release certificate supplies legal first-use bounds; only commuting
CXs may exchange order.  No noisy score is inferred from these binary maps.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[key]='1'
import argparse,json,random,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import a_factory as af
from ortools.sat.python import cp_model

def canonical(rows,width):
    piv={}
    for j in range(width):
        v=sum(1<<q for q,r in rows.items() if r>>j&1)
        while v:
            k=v.bit_length()-1
            if k in piv:v^=piv[k]
            else:piv[k]=v;break
    for j in sorted(piv):
        for k in sorted(piv):
            if k>j and piv[k]>>j&1:piv[k]^=piv[j]
    return tuple(piv[k] for k in sorted(piv))

def construct(rng,direct,root_pool=None):
    width=4 if direct else 3
    masks=[85,102,120,7]
    target={q:(sum(1<<j for j,m in enumerate(masks) if m>>af.A.index(q)&1) if q in af.A else 0) for q in af.CELLS} if direct else af.TARGET.copy()
    # Choose a random invertible generator basis, preserving the state.
    basis=[1<<j for j in range(width)]
    for _ in range(20):
        a,b=rng.sample(range(width),2);basis[b]^=basis[a]
    rows={q:sum(((v&b).bit_count()&1)<<j for j,b in enumerate(basis)) for q,v in target.items()}
    back=[];locked=set();order=list(range(width));rng.shuffle(order)
    for j in order:
        allowed=set(af.CELLS)-locked;terms=[q for q in allowed if rows[q]>>j&1]
        if not terms:continue
        root=rng.choice(terms if root_pool is None else sorted(allowed&set(root_pool)))
        tree=af.tree_for(root,terms,allowed,rng)
        if tree is None:return
        if not rows[root]>>j&1:
            # A free input pivot may start on a helper. Bring one existing
            # column bit to the selected root before filling the tree.
            parent={v:u for u,v in tree};one=next(q for q in [v for _,v in tree] if rows[q]>>j&1)
            path=[];q=one
            while q!=root:path.append((parent[q],q));q=parent[q]
            for u,v in path:
                if not rows[u]>>j&1:rows[u]^=rows[v];back.append((v,u))
        for u,v in tree:
            if not rows[v]>>j&1:rows[v]^=rows[u];back.append((u,v))
        for u,v in reversed(tree):rows[v]^=rows[u];back.append((u,v))
        assert all(not rows[q]>>j&1 for q in allowed if q!=root)
        locked.add(root)
    if sum(bool(v) for v in rows.values())!=width:return
    initial=rows.copy();gates=list(reversed(back));target_sig=canonical(target,width)
    def run(gs):
        rr=initial.copy()
        for u,v in gs:rr[v]^=rr[u]
        return rr
    assert canonical(run(gates),width)==target_sig
    # Delete state-redundant gates, including transformations wholly within
    # the unknown input basis.  The complete output row space is compared.
    indices=list(range(len(gates)));rng.shuffle(indices)
    for i in indices:
        if i>=len(gates):continue
        trial=gates[:i]+gates[i+1:]
        if canonical(run(trial),width)==target_sig:gates=trial
    rr=initial.copy();pruned=[]
    for u,v in gates:
        if rr[u]:pruned.append((u,v));rr[v]^=rr[u]
    assert canonical(rr,width)==target_sig
    return initial,pruned

def schedule(initial,gates,release,states,rng,direct,cp_seconds=0):
    used=set(af.A)|{q for e in gates for q in e}
    plus={q for q,v in initial.items() if v}
    known=lambda q: states[q].get('product_axis')==('X' if q in plus else 'Z') and not states[q].get('phase_xor') and not states[q].get('phase_constant')
    earliest={q:release[q]+int(not known(q)) for q in used}
    pred=[{j for j,(c,d) in enumerate(gates[:i]) if b==c or d==a} for i,(a,b) in enumerate(gates)]
    succ=[set() for _ in gates]
    for i,ps in enumerate(pred):
        for j in ps:succ[j].add(i)
    length=[1]*len(gates)
    for i in range(len(gates)-1,-1,-1):length[i]=1+max((length[j] for j in succ[i]),default=0)
    remaining=set(range(len(gates)));done=set();times=[None]*len(gates);busy={q:earliest[q] for q in used}
    while remaining:
        avail=[i for i in remaining if pred[i]<=done]
        def priority(i):
            a,b=gates[i];t=max(busy[a],busy[b],max((times[j]+1 for j in pred[i]),default=0))
            return (t,-length[i]+rng.random()*.15)
        i=min(avail,key=priority);a,b=gates[i]
        t=max(busy[a],busy[b],max((times[j]+1 for j in pred[i]),default=0))
        times[i]=t;busy[a]=busy[b]=t+1;done.add(i);remaining.remove(i)
    if cp_seconds:
        m=cp_model.CpModel();upper=max(times)+1
        starts=[m.NewIntVar(max(earliest[a],earliest[b]),upper-1,f's{i}') for i,(a,b) in enumerate(gates)]
        ends=[m.NewIntVar(1,upper,f'e{i}') for i in range(len(gates))]
        iv=[]
        for i,(s,e) in enumerate(zip(starts,ends)):m.Add(e==s+1);iv.append(m.NewIntervalVar(s,1,e,f'g{i}'))
        for q in used:m.AddNoOverlap([v for v,e in zip(iv,gates) if q in e])
        for i,ps in enumerate(pred):
            for j in ps:m.Add(starts[i]>=ends[j])
        finish=m.NewIntVar(1,upper,'finish')
        m.AddMaxEquality(finish,[ends[i] for i,e in enumerate(gates) if set(e)&set(af.A)])
        m.Minimize(1000*finish+sum(starts))
        for s,t in zip(starts,times):m.AddHint(s,t)
        sol=cp_model.CpSolver();sol.parameters.num_search_workers=1;sol.parameters.max_time_in_seconds=cp_seconds
        status=sol.Solve(m)
        if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):times=[sol.Value(s) for s in starts]
    # Fully check the reordered physical state map, including helper zeros.
    rr=initial.copy()
    for i in sorted(range(len(gates)),key=lambda i:times[i]):
        a,b=gates[i];rr[b]^=rr[a]
    width=4 if direct else 3
    expected={q:(sum(1<<j for j,m in enumerate([85,102,120,7]) if m>>af.A.index(q)&1) if q in af.A else 0) for q in af.CELLS} if direct else af.TARGET
    assert canonical(rr,width)==canonical(expected,width)
    first={q:min((t for t,e in zip(times,gates) if q in e),default=release[q]+1) for q in used}
    last={q:max((t for t,e in zip(times,gates) if q in e),default=first[q]-1) for q in used}
    operations=[];reuse=[]
    for q in used:
        if first[q]==release[q] and known(q):reuse.append(q)
        else:operations.append(dict(time=first[q]-1,kind='RX' if q in plus else 'R',qs=[q]))
    operations += [dict(time=t,kind='CX',qs=list(e)) for t,e in zip(times,gates)]
    if not direct:operations += [dict(time=last[q]+1,kind='H',qs=[q]) for q in af.A]
    helpers=sorted(used-set(af.A))
    operations += [dict(time=last[q]+1,kind='M',qs=[q],zero_flag=True) for q in helpers]
    return dict(cx=len(gates),a_ready=max(last[q]+(1 if direct else 2) for q in af.A),
        module_end=max(o['time'] for o in operations)+1,direct=direct,helpers=helpers,
        helper_release={q:last[q]+2 for q in helpers},reused_inputs=sorted(reuse),plus_inputs=sorted(plus),
        operations=sorted(operations,key=lambda o:(o['time'],o['kind'],o['qs'])),
        initial_rows=initial,backward_map_verified=True,target='A plusL; borrowed non-A helpers returned to zero and MZ heralded')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--trials',type=int,default=10000);ap.add_argument('--seed',type=int,default=1);ap.add_argument('--cp-seconds',type=float,default=3)
    ap.add_argument('--boundary');ap.add_argument('--states');ap.add_argument('--output');a=ap.parse_args()
    st=time.perf_counter();boundary=json.loads(Path(a.boundary or HERE/'prefix_release.json').read_text());release={int(q):t for q,t in boundary['release'].items()}
    states={r['q']:r for r in json.loads(Path(a.states or HERE/'prefix_product_states.json').read_text())['cells']};rng=random.Random(a.seed)
    candidates=[];seen=set()
    for i in range(a.trials):
        direct=bool(i%2);result=construct(rng,direct)
        if not result:continue
        initial,gates=result;row=schedule(initial,gates,release,states,rng,direct)
        key=(row['a_ready'],row['cx'],tuple(row['plus_inputs']),direct)
        if key in seen:continue
        seen.add(key);row['trial']=i;candidates.append(row)
        if len(candidates)>200:candidates=sorted(candidates,key=lambda r:(r['a_ready'],r['cx'],len(r['helpers'])))[:100]
    candidates.sort(key=lambda r:(r['a_ready'],r['cx'],len(r['helpers'])))
    for row in candidates[:10]:
        gates=[tuple(o['qs']) for o in row['operations'] if o['kind']=='CX']
        initial={int(q):v for q,v in row['initial_rows'].items()};opt=schedule(initial,gates,release,states,rng,row['direct'],a.cp_seconds)
        if opt['a_ready']<=row['a_ready']:row.update(opt)
    candidates.sort(key=lambda r:(r['a_ready'],r['cx'],len(r['helpers'])))
    out=dict(prefix_stem=boundary['stem'],trials=a.trials,seed=a.seed,seconds=time.perf_counter()-st,candidates=candidates[:30])
    Path(a.output or HERE/'a_factory_search.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({**{k:v for k,v in out.items() if k!='candidates'},'best':[{k:r[k] for k in ('a_ready','module_end','cx','direct','plus_inputs','helpers')} for r in candidates[:10]]}),flush=True)

if __name__=='__main__':main()
