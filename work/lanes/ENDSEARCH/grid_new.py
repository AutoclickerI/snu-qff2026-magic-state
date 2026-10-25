"""Exact fixed-cell template packing and whole-resource CSS synthesis on 6x6.
Placement is CP-SAT. CNOT synthesis is the SQUARE lane's reverse GF(2)
Steiner elimination, generalized to four ancillary blocks. No resource or idle
noise is omitted. Failed first-order checks remain failed builds.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,itertools,random,sys,copy
from collections import deque
from ortools.sat.python import cp_model
from build_candidates import H,prefix,GENS,finish,save

def nb(a,b):return abs(a//6-b//6)+abs(a%6-b%6)==1

def paths(g,root):
    found={root:[root]};todo=deque([root])
    while todo:
        a=todo.popleft()
        for b in g[a]:
            if b not in found:found[b]=found[a]+[b];todo.append(b)
    return found

def placements(t):
    edges={tuple(sorted(e)) for l in t['layers'] for e in l};n=t['n'];out=[]
    def rec(v):
        if len(v)==n:out.append(tuple(v[b] for b in range(n)));return
        b=min((b for b in range(n) if b not in v),key=lambda b:-sum(tuple(sorted((a,b))) in edges for a in v))
        for q in range(36):
            if q in v.values():continue
            if all(nb(q,p) for a,p in v.items() if tuple(sorted((a,b))) in edges):rec(dict(v,**{str(b):q}))
    # Integer keys avoid Python's keyword-key coercion.
    def walk(v):
        if len(v)==n:out.append(tuple(v[b] for b in range(n)));return
        b=max((b for b in range(n) if b not in v),key=lambda b:sum(tuple(sorted((a,b))) in edges for a in v))
        for q in range(36):
            if q in v.values():continue
            if all(nb(q,p) for a,p in v.items() if tuple(sorted((a,b))) in edges):
                v[b]=q;walk(v);del v[b]
    walk({});return out

def layout(t,D,maxmove=1):
    ps=placements(t);m=cp_model.CpModel();chosen=[];cell={q:[] for q in range(36)};obj=[]
    for i,d in enumerate(D):
        vs=[]
        for j,p in enumerate(ps):
            if p[0] in set(D)-{d}:continue
            distance=abs(p[0]//6-d//6)+abs(p[0]%6-d%6)
            if distance>maxmove:continue
            x=m.NewBoolVar(f'{i}_{j}');vs.append((x,p));obj.append(distance*x)
            for q in p:cell[q].append(x)
        m.AddExactlyOne(x for x,p in vs);chosen.append(vs)
    for xs in cell.values():m.AddAtMostOne(xs)
    m.Minimize(sum(obj));sol=cp_model.CpSolver();sol.parameters.num_search_workers=1
    st=sol.Solve(m)
    if st==cp_model.INFEASIBLE and maxmove<10:return layout(t,D,maxmove+1)
    assert st in (cp_model.OPTIMAL,cp_model.FEASIBLE),sol.StatusName(st)
    pp=[next(p for x,p in vs if sol.Value(x)) for vs in chosen]
    return [[p[b] for p in pp] for b in range(t['n'])],dict(status=sol.StatusName(st),data_hops=sol.ObjectiveValue(),placements=len(ps))

def synth(t,blocks,release,seed):
    rng=random.Random(seed);D=blocks[0];sites=[q for q in range(36) if q not in D];graph={q:[b for b in sites if nb(q,b)] for q in sites}
    assert len(paths(graph,sites[0]))==len(sites),'non-data graph disconnected'
    for xs in graph.values():rng.shuffle(xs)
    rows=[{block[i] for i in g} for b,block in enumerate(blocks[1:],1) for g in GENS+([{0,1,2}] if t['product_plus_mask']>>(b-1)&1 else [])]
    x={q:sum((q in row)<<j for j,row in enumerate(rows)) for q in sites};available=sites.copy();ops=[];piv=[]
    for j in range(len(rows)):
        g={a:[b for b in graph[a] if b in available] for a in available};roots=[]
        for q in available:
            gg={a:[b for b in g[a] if b!=q] for a in available if a!=q}
            if len(paths(gg,next(iter(gg))))==len(available)-1:roots.append(q)
        choices=[]
        pp={a:paths(g,a) for a in available}
        for bit in range(len(rows)):
            terminals={q for q in available if x[q]>>bit&1}
            if not terminals:continue
            for root in roots:
                tree={root:set()};todo=terminals-{root}
                while todo:
                    p=min((pp[a][q] for a in tree for q in todo),key=lambda p:len(p)+rng.random()*.03)
                    for a,b in zip(p,p[1:]):tree.setdefault(a,set()).add(b);tree.setdefault(b,set()).add(a)
                    todo-=set(p)
                cost=2*(len(tree)-1)-len(terminals)+int(root in terminals)
                choices.append((cost+rng.random()*3+.06*release[root],bit,root,tree))
        _,bit,root,tree=min(choices,key=lambda x:x[0]);order=[];parent={root:None};queue=deque([root])
        while queue:
            a=queue.popleft();order.append(a)
            for b in tree[a]:
                if b not in parent:parent[b]=a;queue.append(b)
        def cx(a,b):ops.append((a,b));x[b]^=x[a]
        for b in reversed(order[1:]):
            a=parent[b]
            if not (x[a]>>bit&1):cx(b,a)
        for b in reversed(order[1:]):cx(parent[b],b)
        piv.append(root);available.remove(root)
    assert all(x[q]==0 for q in available)
    y={q:(1<<piv.index(q)) if q in piv else 0 for q in sites}
    for a,b in reversed(ops):y[b]^=y[a]
    def rank(vs):
        basis={}
        for v in vs:
            while v:
                k=v.bit_length()-1
                if k in basis:v^=basis[k]
                else:basis[k]=v;break
        return len(basis)
    want=[sum(1<<q for q in row) for row in rows]
    got=[sum(((y[q]>>j)&1)<<q for q in sites) for j in range(len(piv))]
    assert rank(got)==len(rows)==rank(got+want)
    return list(reversed(ops)),set(piv)

def build(t,label,blocks,seed,jit=False):
    c,D,release=prefix()
    live=set(D)
    for a,b in zip(D,blocks[0]):
        if a!=b:
            assert b not in live
            g={q:[r for r in range(36) if r not in live-{a} and nb(q,r)] for q in range(36) if q not in live-{a}}
            path=paths(g,a)[b];tt=44
            for u,v in zip(path,path[1:]):
                tt=max(tt,release[v]+1);c.reset(tt-1,v);c.cx(tt,u,v);c.cx(tt+1,v,u);c.dets.append([c.read(tt+2,u)])
                release[u]=tt+3;release[v]=tt+2;tt+=2
            live.remove(a);live.add(b)
    ops,piv=synth(t,blocks,release,seed);sites=[q for q in range(36) if q not in blocks[0]];end={q:release[q]+1 for q in sites};first={};last={}
    for a,b in ops:
        tt=max(end[a],end[b]);c.cx(tt,a,b)
        for q in (a,b):first.setdefault(q,tt);last[q]=tt;end[q]=tt+1
    for q,tt in first.items():c.reset(tt-1,q,q in piv)
    for q in sites:
        if q not in first:c.reset(release[q],q,q in piv)
    R=max(max(end.values()),max(release[q] for q in blocks[0]))
    if jit:
        firstuse={b:min(k for k,l in enumerate(t['layers']) if any(b in e for e in l)) for b in range(t['n'])}
        R=max([max(release[q] for q in blocks[0])-firstuse[0]]+[max(end[q] for q in block)-firstuse[b] for b,block in enumerate(blocks[1:],1)])
    for q in set(sites)-set(sum(blocks[1:],[])):
        c.dets.append([c.read(end[q],q)])
    finish(c,t,blocks,R)
    name=save(c,f'grid_{label}_{"jit_" if jit else ""}s{seed}',t,blocks,round_start=R,change='CP-SAT packed template; grid GF2 CSS preparation; v37b causal prefix; all noise',prep_cx=len(ops),seed=seed,just_in_time_preparations=jit)
    p=H/'builds'/f'{name}.json';m=json.loads(p.read_text());m['grid_free']=False;p.write_text(json.dumps(m,indent=2)+'\n')
    return dict(name=name,R=R,prep_cx=len(ops))

if __name__=='__main__':
    choices=json.loads((H/'choices.json').read_text());_,D,_=prefix();out={}
    for label in ('tree','square_leaf'):
        t=choices[label];blocks,proof=layout(t,D);print(label,blocks,proof,flush=True)
        results=[build(t,label,blocks,seed) for seed in range(8)]
        results.sort(key=lambda x:(x['R'],x['prep_cx']));out[label]=dict(roles=blocks,placement=proof,builds=results)
        (H/'grid_manifest.json').write_text(json.dumps(out,indent=2)+'\n')
        print(label,results,flush=True)
