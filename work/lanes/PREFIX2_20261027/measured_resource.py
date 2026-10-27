"""Native CSS resource seeds with measured spare parities.

The primary target is the rank-seven dual-A/BC resource for the four-square
terminal. Spare cells need not be coherently returned to zero: their X reads
induce known Z byproducts before the final A Hadamards. The complete circuit
assembler derives the corresponding affine measurement-record checks.

These are state-preparation witnesses. No fault-tolerance or score is inferred
from the binary map; full raw-state and noisy audits are separate steps.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse,json,random,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'work/lanes/NATIVE2_20261027'))
sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
import a_factory as af
from a_factory_search import canonical
from partial_contract import make_four_square_contract,make_partial_contract
from terminal_variants import make_variant
from resource_pauli_audit import audit


def construct(pc,rng,release,mix=False,prune_passes=3,fill_mode=0,basis_steps=20,protect=0,root_any=False):
    width=pc.rank;target=pc.COLS.copy()
    cells=sorted(target);core={q for q,v in target.items() if v}
    protected={q for q in set(cells)-core if rng.random()<protect}
    # Blockwise basis changes keep A and BC spatially simple. Occasional full
    # changes expose equivalent mixed input bases without changing the target.
    basis=[1<<j for j in range(width)]
    for _ in range(basis_steps):
        pool=list(range(width)) if mix else rng.choice([list(range(3)),list(range(3,width))])
        if len(pool)<2:continue
        a,b=rng.sample(pool,2);basis[b]^=basis[a]
    rows={q:sum(((v&b).bit_count()&1)<<j for j,b in enumerate(basis)) for q,v in target.items()}
    # The measured spare rows are free. Fill Steiner vertices in a generator
    # support instead of requiring every borrowed wire to finish at zero.
    if fill_mode==1:
        for j in range(width):
            terms=[q for q in core if rows[q]>>j&1]
            tree=af.tree_for(rng.choice(terms),terms,set(cells),rng)
            if tree is None:return
            for a,b in tree:
                for q in (a,b):
                    if q not in core and q not in protected:rows[q]|=1<<j
    elif fill_mode==2:
        remaining=set(cells)-core
        while remaining:
            available=[q for q in remaining if any(v in rows and v not in remaining and rows[v] for v in af.ADJ[q])]
            if not available:break
            q=rng.choice(available);neighbors=[v for v in af.ADJ[q] if v in rows and v not in remaining and rows[v]]
            if q not in protected:rows[q]=rows[rng.choice(neighbors)]
            remaining.remove(q)
    back=[];locked=set();order=list(range(width));rng.shuffle(order)
    for j in order:
        allowed=set(cells)-locked;terms=[q for q in allowed if rows[q]>>j&1]
        if not terms:continue
        roots=sorted(allowed) if root_any else terms
        root=rng.choices(roots,weights=[1/(1+max(0,release[q]-8)*.15) for q in roots])[0]
        tree=af.tree_for(root,terms,allowed,rng)
        if tree is None:return
        if not rows[root]>>j&1:
            parents={v:u for u,v in tree}
            one=next(q for q in [v for _,v in tree] if rows[q]>>j&1)
            path=[];q=one
            while q!=root:path.append((parents[q],q));q=parents[q]
            for u,v in path:
                if not rows[u]>>j&1:rows[u]^=rows[v];back.append((v,u))
        for u,v in tree:
            if not rows[v]>>j&1:rows[v]^=rows[u];back.append((u,v))
        for u,v in reversed(tree):rows[v]^=rows[u];back.append((u,v))
        if any(rows[q]>>j&1 for q in allowed if q!=root):raise AssertionError('elimination failed')
        locked.add(root)
    if sum(bool(v) for v in rows.values())!=width:return
    initial=rows.copy();gates=list(reversed(back))
    expected=canonical({q:target[q] for q in core},width)
    def run(gs):
        rr=initial.copy()
        for u,v in gs:rr[v]^=rr[u]
        return rr
    def valid(gs):
        rr=run(gs)
        return not any(rr[q] for q in protected) and canonical({q:rr[q] for q in core},width)==expected
    assert valid(gates)
    for _ in range(prune_passes):
        order=list(range(len(gates)));rng.shuffle(order);changed=False
        for i in order:
            if i>=len(gates):continue
            test=gates[:i]+gates[i+1:]
            if valid(test):gates=test;changed=True
        if not changed:break
    rr=initial.copy();pruned=[]
    for a,b in gates:
        if rr[a]:rr[b]^=rr[a];pruned.append((a,b))
    assert valid(pruned)
    return initial,pruned,rr


def support(row,final,core):
    # A spare row is a known parity of target variables. Return a physical
    # Z operator inducing that parity; after A H its A factors become X.
    best={0:[]}
    for q in sorted(core):
        for v,qs in list(best.items()):
            nv=v^final[q];ns=qs+[q]
            if nv not in best or len(ns)<len(best[nv]):best[nv]=ns
    if row not in best:raise ValueError('Spare parity has an independent variable')
    return best[row]


def schedule(pc,initial,gates,final,release,states,rng,preserve_wire_order=False):
    core={q for q,v in pc.COLS.items() if v};used=core|{q for e in gates for q in e}
    plus={q for q,v in initial.items() if v}
    def known(q):
        s=states[q]
        return s.get('product_axis')==('X' if q in plus else 'Z') and not s.get('phase_constant') and (q in plus or not s.get('phase_xor'))
    earliest={q:release[q]+int(not known(q)) for q in used}
    pred=[{j for j,(c,d) in enumerate(gates[:i]) if b==c or d==a} for i,(a,b) in enumerate(gates)]
    if preserve_wire_order:
        pred=[{j for j,e in enumerate(gates[:i]) if set(e)&set(edge)} for i,edge in enumerate(gates)]
    succ=[set() for _ in gates]
    for i,ps in enumerate(pred):
        for j in ps:succ[j].add(i)
    length=[1]*len(gates)
    for i in range(len(gates)-1,-1,-1):length[i]=1+max((length[j] for j in succ[i]),default=0)
    remaining=set(range(len(gates)));done=set();times=[None]*len(gates);busy=earliest.copy()
    while remaining:
        choices=[i for i in remaining if pred[i]<=done]
        def key(i):
            a,b=gates[i];t=max(busy[a],busy[b],max((times[j]+1 for j in pred[i]),default=0))
            return t,-length[i]+rng.random()*.1
        i=min(choices,key=key);a,b=gates[i]
        t=max(busy[a],busy[b],max((times[j]+1 for j in pred[i]),default=0))
        times[i]=t;busy[a]=busy[b]=t+1;done.add(i);remaining.remove(i)
    first={q:min((t for t,e in zip(times,gates) if q in e),default=release[q]+1) for q in used}
    last={q:max((t for t,e in zip(times,gates) if q in e),default=first[q]-1) for q in used}
    operations=[];reused=[];source_phases=[]
    for q in used:
        if first[q]==release[q] and known(q):
            reused.append(q)
            if states[q].get('phase_xor'):source_phases.append(dict(q=q,bits=states[q]['phase_xor']))
        else:operations.append(dict(time=first[q]-1,kind='RX' if q in plus else 'R',qs=[q]))
    operations += [dict(time=t,kind='CX',qs=list(e)) for t,e in zip(times,gates)]
    helpers=sorted(used-core);corrections=[]
    for q in helpers:
        parity=support(final[q],final,core)
        row=dict(time=last[q]+1,kind='MX' if final[q] else 'M',qs=[q],zero_flag=not final[q])
        operations.append(row)
        if parity:corrections.append(dict(helper=q,time=row['time'],X=[z for z in parity if z in pc.post_h],Z=[z for z in parity if z not in pc.post_h]))
    operations += [dict(time=last[q]+1,kind='H',qs=[q]) for q in pc.post_h]
    ready=max(o['time']+1 for o in operations)
    for q in pc.late_plus:
        t=max(release[q],last.get(q,-1)+2,ready-1)
        operations.append(dict(time=t,kind='RX',qs=[q]));ready=max(ready,t+1)
    # Replay actual commuting schedule, not only the original gate ordering.
    rr=initial.copy()
    for i in sorted(range(len(gates)),key=lambda i:times[i]):
        a,b=gates[i];rr[b]^=rr[a]
    assert rr==final
    return dict(cx=len(gates),resource_ready=ready,module_end=ready,helpers=helpers,
        helper_byproducts=corrections,reused_inputs=reused,source_phases=source_phases,
        plus_inputs=sorted(plus),initial_rows=initial,final_rows=final,
        target_columns=pc.COLS,resource_rank=pc.rank,dual_a=pc.dual_a,
        operations=sorted(operations,key=lambda o:(o['time'],o['kind'],o['qs'])),
        native_map_verified=True,scope='Native ideal resource witness; requires complete raw and noisy audits')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--trials',type=int,default=200);ap.add_argument('--seed',type=int,default=0)
    ap.add_argument('--boundary',default=str(ROOT/'work/lanes/NATIVE2_20261027/prefix_release.json'))
    ap.add_argument('--states',default=str(ROOT/'work/lanes/NATIVE2_20261027/prefix_product_states.json'))
    ap.add_argument('--contract');ap.add_argument('--mask',type=lambda x:int(x,0),default=25);ap.add_argument('--swap',type=lambda x:int(x,0),default=0)
    ap.add_argument('--basis-steps',type=int,default=20);ap.add_argument('--protect',type=float,default=0.)
    ap.add_argument('--risk',action='store_true');ap.add_argument('--output',default=str(HERE/'measured_resource.json'))
    args=ap.parse_args();start=time.perf_counter()
    boundary=json.loads(Path(args.boundary).read_text());release={int(q):v for q,v in boundary['release'].items()}
    states={r['q']:r for r in json.loads(Path(args.states).read_text())['cells']}
    if args.contract:
        cfg=json.loads(Path(args.contract).read_text());pc=make_partial_contract(cfg['roles'],cfg['square_mask'],True,True)
    else:pc=make_variant(args.mask,args.swap,True,True)
    rng=random.Random(args.seed);candidates=[];seen=set()
    for i in range(args.trials):
        result=construct(pc,rng,release,mix=i%8==7,fill_mode=i%3,basis_steps=args.basis_steps,protect=args.protect)
        if not result:continue
        row=schedule(pc,*result,release,states,rng);row['trial']=i;row['fill_mode']=i%3
        if args.risk:row['resource_c1']=audit(pc,row)['resource_c1']
        key=(row['resource_ready'],row['cx'],tuple(row['plus_inputs']),tuple(row['helpers']))
        if key in seen:continue
        seen.add(key);candidates.append(row)
        candidates.sort(key=lambda r:(r.get('resource_c1',0),r['resource_ready'],r['cx']))
        candidates=candidates[:25]
        if i%200==0:print(json.dumps(dict(trial=i,best=[{k:r[k] for k in ['resource_ready','cx','plus_inputs','resource_c1'] if k in r} for r in candidates[:3]])),flush=True)
    out=dict(prefix_stem=boundary['stem'],roles=pc.roles,square_mask=pc.square_mask,dual_a=True,
        terminal_operations=pc.terminal(),drop_free=True,swap_mask=args.swap,
        boundary_file=args.boundary,states_file=args.states,seed=args.seed,trials=args.trials,protect_fraction=args.protect,
        seconds=time.perf_counter()-start,candidates=candidates)
    Path(args.output).write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(output=args.output,seconds=out['seconds'],best=[{k:r[k] for k in ['resource_ready','cx','helpers','plus_inputs','resource_c1'] if k in r} for r in candidates[:5]])),flush=True)


if __name__=='__main__':main()
