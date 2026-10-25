"""Local GF(2) state synthesis on the entire square resource graph.

Eliminate a generator column along a Steiner tree, then remove a non-cut
pivot vertex. Reverse the elimination to prepare the desired CSS subspace.
Column basis changes are free descriptions of the same subspace, not gates.
"""
import json,sys,random,copy,itertools,multiprocessing as mp
from collections import deque
from build_rounds import H,GENS
import build_suffix as S
from route_grid import nb

def paths(graph,root):
    found={root:[root]};todo=deque([root])
    while todo:
        a=todo.popleft()
        for b in graph[a]:
            if b not in found:found[b]=found[a]+[b];todo.append(b)
    return found

def bridge(path):
    if len(path)==2:return [tuple(path)]
    d=len(path)-1
    return [(path[i],path[i+1]) for i in range(d)]+[(path[i],path[i+1]) for i in reversed(range(d-1))]+[(path[i],path[i+1]) for i in range(1,d)]+[(path[i],path[i+1]) for i in reversed(range(1,d-1))]

def synth(seed):
    rng=random.Random(seed);lay=json.loads((H/'layout_joint.json').read_text())
    D,A,B,C=[lay[k] for k in ('D','A','B','C')]
    sites=[q for q in range(36) if q not in D]
    graph={a:[b for b in sites if nb(a,b)] for a in sites}
    for v in graph.values():rng.shuffle(v)
    rows=[{b[i] for i in row} for b,gs in [(A,GENS+[{0,1,2}]),(B,GENS),(C,GENS+[{0,1,2}])] for row in gs]
    x={q:sum((q in row)<<j for j,row in enumerate(rows)) for q in sites}
    available=sites.copy();ops=[];piv=[]
    for j in range(len(rows)):
        g={a:[b for b in graph[a] if b in available] for a in available}
        roots=[q for q in available if len(paths({a:[b for b in g[a] if b!=q] for a in available if a!=q},next(a for a in available if a!=q)))==len(available)-1]
        choices=[]
        for bit in range(len(rows)):
            terminals={q for q in available if x[q]>>bit&1}
            if not terminals:continue
            for root in roots:
                # Incrementally attach the closest remaining terminal to the tree.
                tree={root:set()};todo=terminals-{root}
                while todo:
                    pp=[p for a in tree for q,p in paths(g,a).items() if q in todo]
                    p=min(pp,key=lambda p:len(p)+rng.random()*.03)
                    for a,b in zip(p,p[1:]):tree.setdefault(a,set()).add(b);tree.setdefault(b,set()).add(a)
                    todo-=set(p)
                cost=2*(len(tree)-1)-len(terminals)+int(root in terminals)
                score=cost + rng.random()*3 + .06*S.release[root]
                choices.append((score,bit,root,tree))
        _,bit,root,tree=min(choices,key=lambda a:a[0])
        order=[];parent={root:None};queue=deque([root])
        while queue:
            a=queue.popleft();order.append(a)
            for b in tree[a]:
                if b not in parent:parent[b]=a;queue.append(b)
        def cx(a,b):ops.append((a,b));x[b]^=x[a]
        for b in reversed(order[1:]):
            a=parent[b]
            if not (x[a]>>bit&1):
                assert x[b]>>bit&1;cx(b,a)
        for b in reversed(order[1:]):
            a=parent[b];assert x[a]>>bit&1 and x[b]>>bit&1;cx(a,b)
        assert x[root]>>bit&1
        assert all(not(x[q]>>bit&1) for q in available if q!=root)
        piv.append(root);available.remove(root)
    assert all(x[q]==0 for q in available)
    # Verify the physical preparation span independently of generator labels.
    y={q:1<<piv.index(q) if q in piv else 0 for q in sites}
    for a,b in reversed(ops):y[b]^=y[a]
    span={0}
    target=[sum((q in row)<<sites.index(q) for q in sites) for row in rows]
    for v in target:span|={a^v for a in list(span)}
    for j in range(len(piv)):
        assert sum(((y[q]>>j)&1)<<sites.index(q) for q in sites) in span
    helpers=[q for q in sites if q not in A+B+C]
    logical=[s for s in itertools.combinations(range(7),3) if all(len(set(s)&g)%2==0 for g in GENS)]
    choices=[]
    for flag in helpers:
        for support in logical:
            checks=[bridge(paths(graph,B[i])[flag]) for i in support]
            choices.append((sum(map(len,checks)),flag,support,checks))
    _,flag,support,checks=min(choices)
    return dict(seed=seed,pivots=piv,ops=list(reversed(ops)),flag=flag,support=support,checks=checks,prep_cx=len(ops))

def build(resource,tag='gf2',layout='layout_joint.json',alap=False,guards=False):
    lay=json.loads((H/layout).read_text());D,A,B,C=[lay[k] for k in ('D','A','B','C')]
    sites=[q for q in range(36) if q not in D];helpers=[q for q in sites if q not in A+B+C]
    c=S.prefix();release=S.release.copy()
    for path in lay['paths'].values():
        t=44
        for a,b in zip(path,path[1:]):
            t=max(t,release[b]+1);c.reset(t-1,b);c.cx(t,a,b);c.cx(t+1,b,a)
            c.dets.append([c.read(t+2,a)]);release[a]=t+3;t+=2
    end={q:release[q]+1 for q in sites};first={};last={};schedule=[];plan=[]
    for op in resource['ops']+[e for check in resource['checks'] for e in check]:
        if isinstance(op,dict):
            t=max(end[q] for q in op['barrier'])
            for q in op['barrier']:end[q]=t
            plan.append(op);continue
        a,b=op
        t=max(end[a],end[b]);schedule.append((t,a,b))
        plan.append((t,a,b))
        for q in (a,b):first.setdefault(q,t);last[q]=t;end[q]=t+1
    R=max(max(end[q] for q in A+B+C),max(lay['arrival'].values()),last[resource['flag']]+2)
    if alap:
        latest={q:R-1 if q in A+B+C else R-2 for q in sites};ss=[]
        for op in reversed(plan):
            if isinstance(op,dict):
                t=min(latest[q] for q in op['barrier'])
                for q in op['barrier']:latest[q]=t
                continue
            _,a,b=op
            t=min(latest[a],latest[b]);ss.append((t,a,b));latest[a]=latest[b]=t-1
        schedule=list(reversed(ss));first={};last={}
        for t,a,b in schedule:
            for q in (a,b):first.setdefault(q,t);last[q]=t
        assert all(first[q]>release[q] for q in first)
    for t,a,b in schedule:c.cx(t,a,b)
    for q,t in first.items():c.reset(t-1,q,q in resource['pivots'])
    for q in A+B+C:
        if q not in first:c.reset(R-1,q,q in resource['pivots'])
    for q in helpers:
        if q in last:c.dets.append([c.read(last[q]+1,q)])
    guard_list=[]
    if guards:
        useddata=set()
        options=sorted((last.get(q,release[q])+3,q,d) for q in helpers for d in D if nb(q,d))
        usedhelpers=set()
        for start,q,d in options:
            if q in usedhelpers or d in useddata:continue
            start=max(start,lay['arrival'][str(D.index(d))] if str(D.index(d)) in lay['arrival'] else lay['arrival'][D.index(d)])
            if start>R-1:continue
            c.reset(start-1,q,True)
            for t in range(start,R):c.cx(t,d,q)
            c.dets.append([c.read(R,q,True)]);guard_list.append(dict(helper=q,data=d,start=start,end=R-1));useddata.add(d);usedhelpers.add(q)
    for d,a,b,cc in zip(D,A,B,C):c.cx(R,d,a);c.cx(R,b,cc);c.cx(R+1,b,d);c.cx(R+1,cc,a)
    c.readblock(R+2,A);c.readblock(R+2,B,True);c.readblock(R+2,C,True,True)
    name=f'grid_{tag}_s{resource["seed"]}'
    c.save(name,roles=dict(D=D,A=A,B=B,C=C),round_start=R,change='local GF(2) joint CSS synthesis + explicit B logical-Z bridge verification',
        resource=resource,preparation_ops=schedule,layout=layout,alap=alap,guards=guard_list)
    p=H/'builds'/f'{name}.json';md=json.loads(p.read_text());md['data_qubits']=D;md['grid_free']=False;p.write_text(json.dumps(md,indent=2)+'\n')
    oo,_=S.parse_current(p.with_suffix('.qasm').read_text());used=set()
    for o in oo:
        keys={(o.time,q) for q in o.qs};assert not used&keys,(name,o,used&keys);used|=keys
        if o.kind=='CX':assert nb(*o.qs)
    return dict(name=name,R=R,prep_cx=resource['prep_cx'],verification_cx=sum(map(len,resource['checks'])),seed=resource['seed'])

if __name__=='__main__':
    count=int(sys.argv[1]) if len(sys.argv)>1 else 64
    with mp.get_context('fork').Pool(7) as pool:resources=list(pool.imap(synth,range(count)))
    rows=[build(r) for r in resources];rows.sort(key=lambda r:(r['R'],r['prep_cx']))
    (H/'gf2_manifest.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows[:10]),flush=True)
