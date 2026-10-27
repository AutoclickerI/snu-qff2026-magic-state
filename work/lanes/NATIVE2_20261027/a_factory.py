"""Construct native A=|+L> factories with borrowed cells returned to zero.

State-specific Steiner elimination reduces the three-generator |0L> support
to product inputs, then reverses the local CX sequence and applies H on A.
The schedule respects the measured source release times and checks reuse of
known product inputs against official exact-state evidence.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,heapq,json,random,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'work/tools'));sys.path.insert(0,str(ROOT/'work/lanes/END2_20261027'))
from partial_contract import A,D

CELLS=sorted(set(range(36))-set(D))
ADJ={q:[v for v in CELLS if abs(q//6-v//6)+abs(q%6-v%6)==1] for q in CELLS}
TARGET={q:(A.index(q)+1 if q in A else 0) for q in CELLS}

def signature(rows):
    vectors=[sum(1<<q for q,v in rows.items() if v>>j&1) for j in range(3)];piv={}
    for v in vectors:
        while v:
            j=v.bit_length()-1
            if j in piv:v^=piv[j]
            else:piv[j]=v;break
    for j in sorted(piv):
        for k in sorted(piv):
            if k>j and piv[k]>>j&1:piv[k]^=piv[j]
    return tuple(piv[j] for j in sorted(piv))

def tree_for(root,terminals,allowed,rng):
    weights={tuple(sorted((u,v))):rng.uniform(.7,1.3) for u in allowed for v in ADJ[u] if v in allowed}
    tree={root};edges=[];todo=set(terminals)-tree
    while todo:
        dist={q:0. for q in tree};parent={};heap=[(0.,q) for q in tree];heapq.heapify(heap);found=None
        while heap:
            d,u=heapq.heappop(heap)
            if d!=dist[u]:continue
            if u in todo:found=u;break
            for v in ADJ[u]:
                if v not in allowed:continue
                nd=d+weights[tuple(sorted((u,v)))]
                if nd<dist.get(v,1e99):dist[v]=nd;parent[v]=u;heapq.heappush(heap,(nd,v))
        if found is None:return None
        u=found;path=[]
        while u not in tree:
            v=parent[u];path.append((v,u));u=v
        for u,v in reversed(path):edges.append((u,v));tree.add(v)
        todo-=tree
    adj={q:[] for q in tree}
    for u,v in edges:adj[u].append(v);adj[v].append(u)
    ordered=[]
    def walk(u,p=None):
        for v in adj[u]:
            if v==p:continue
            ordered.append((u,v));walk(v,u)
    walk(root)
    return ordered

def construct(rng):
    rows=TARGET.copy();back=[];locked=set();order=[0,1,2];rng.shuffle(order)
    for j in order:
        allowed=set(CELLS)-locked;terms=[q for q in allowed if rows[q]>>j&1]
        if not terms:continue
        root=rng.choice(terms);tree=tree_for(root,terms,allowed,rng)
        if tree is None:return None
        for u,v in tree:
            if not rows[v]>>j&1:rows[v]^=rows[u];back.append((u,v))
        for u,v in reversed(tree):rows[v]^=rows[u];back.append((u,v))
        assert all(not rows[q]>>j&1 for q in allowed if q!=root)
        locked.add(root)
    if sum(bool(v) for v in rows.values())!=3:return None
    gates=list(reversed(back));initial=rows.copy();target_sig=signature(TARGET)
    def run(gs):
        rr=initial.copy()
        for u,v in gs:rr[v]^=rr[u]
        return rr
    assert signature(run(gates))==target_sig
    # State-specific deletions are checked against the complete CSS row space,
    # rather than a fixed linear-unitary map on unused product inputs.
    for _ in range(2):
        changed=False;indices=list(range(len(gates)));rng.shuffle(indices)
        for i in indices:
            if i>=len(gates):continue
            test=gates[:i]+gates[i+1:]
            if signature(run(test))==target_sig:gates=test;changed=True
        if not changed:break
    rr=initial.copy();pruned=[]
    for u,v in gates:
        if rr[u]:pruned.append((u,v));rr[v]^=rr[u]
    assert signature(rr)==target_sig
    return initial,pruned

def schedule(initial,gates,release,states):
    used=set(A)|{q for g in gates for q in g}
    def known(q,axis):
        s=states[q]
        return s.get('product_axis')==axis and not s.get('phase_xor') and not s.get('phase_constant')
    plus={q for q,v in initial.items() if v};free={q:release[q]+int(not known(q,'X' if q in plus else 'Z')) for q in used}
    times=[];first={};last={}
    for u,v in gates:
        t=max(free[u],free[v]);times.append(t)
        for q in (u,v):first.setdefault(q,t);last[q]=t;free[q]=t+1
    operations=[];reuse=[]
    for q in used:
        if q not in first:first[q]=release[q]+1;last[q]=first[q]-1
        if first[q]==release[q] and known(q,'X' if q in plus else 'Z'):reuse.append(q)
        else:operations.append(dict(time=first[q]-1,kind='RX' if q in plus else 'R',qs=[q]))
    operations += [dict(time=t,kind='CX',qs=[u,v]) for t,(u,v) in zip(times,gates)]
    for q in A:operations.append(dict(time=last[q]+1,kind='H',qs=[q]))
    helpers=sorted(used-set(A));end_records=[]
    for q in helpers:
        t=last[q]+1;operations.append(dict(time=t,kind='M',qs=[q],zero_flag=True));end_records.append(dict(q=q,time=t))
    return dict(cx=len(gates),a_ready=max(last[q]+2 for q in A),module_end=max(o['time'] for o in operations)+1,
        helpers=helpers,helper_release={q:last[q]+2 for q in helpers},reused_inputs=sorted(reuse),
        plus_inputs=sorted(plus),operations=sorted(operations,key=lambda o:(o['time'],o['kind'],o['qs'])),
        target='A plusL; borrowed non-A cells returned to zero and heralded in Z')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--trials',type=int,default=200);ap.add_argument('--seed',type=int,default=1);args=ap.parse_args()
    st=time.perf_counter();boundary=json.loads((HERE/'prefix_release.json').read_text());release={int(q):t for q,t in boundary['release'].items()}
    states={r['q']:r for r in json.loads((HERE/'prefix_product_states.json').read_text())['cells']}
    rng=random.Random(args.seed);candidates=[];seen=set()
    for i in range(args.trials):
        result=construct(rng)
        if result is None:continue
        initial,gates=result;candidate=schedule(initial,gates,release,states)
        key=(candidate['a_ready'],candidate['cx'],tuple(candidate['helpers']))
        if key not in seen:
            seen.add(key);candidate.update(trial=i,initial_rows=initial,backward_map_verified=True);candidates.append(candidate)
    candidates.sort(key=lambda r:(r['a_ready'],r['cx'],len(r['helpers'])))
    out=dict(prefix_stem=boundary['stem'],trials=args.trials,seconds=time.perf_counter()-st,seed=args.seed,candidates=candidates[:20])
    (HERE/'a_factory_seeds.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(dict(trials=args.trials,seconds=out['seconds'],best=[{k:r[k] for k in ('trial','a_ready','module_end','cx','helpers','helper_release','plus_inputs','reused_inputs')} for r in candidates[:10]]),indent=2),flush=True)

if __name__=='__main__':main()
