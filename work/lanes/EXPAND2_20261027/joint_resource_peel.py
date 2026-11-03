"""Constructive native CSS preparation by parity elimination on graph trees.

Eliminate a dependent physical row by computing its expression along a Steiner
tree; internal unselected rows are canceled with a before/after CX. Freeze only
non-articulation vertices, so the remaining graph stays connected. Independent
rows become free plus-state pivots. This guarantees a state witness; noisy
fault-tolerance is reported separately and is not guaranteed.
"""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[key]='1'
import argparse,collections,json,random,sys,time
from pathlib import Path
from joint_resource_beam import finish,safe
import partial_contract as pc
HERE=Path(__file__).resolve().parent


def bfs(start,allowed,adj,targets=None):
    todo=collections.deque([start]);prev={start:None}
    while todo:
        q=todo.popleft()
        if targets is not None and q in targets:
            path=[]
            while q is not None:path.append(q);q=prev[q]
            return list(reversed(path))
        for v in adj[q]:
            if v in allowed and v not in prev:prev[v]=q;todo.append(v)
    return prev


def expression(q,rows,active,adj,rng):
    order=list(active-{q});dist={q:0};todo=collections.deque([q])
    while todo:
        a=todo.popleft()
        for b in adj[a]:
            if b in active and b not in dist:dist[b]=dist[a]+1;todo.append(b)
    order.sort(key=lambda v:dist[v]+rng.random()*2)
    piv={}
    for a in order:
        v=rows[a];wit=1<<a
        while v:
            h=v.bit_length()-1
            if h not in piv:piv[h]=(v,wit);break
            x,w=piv[h];v^=x;wit^=w
    v=rows[q];wit=0
    while v:
        h=v.bit_length()-1
        if h not in piv:return None
        x,w=piv[h];v^=x;wit^=w
    return {a for a in active if wit>>a&1}


def parity_tree(q,selected,active,adj):
    nodes={q};tree=collections.defaultdict(set)
    todo=set(selected)
    while todo:
        paths=[bfs(s,active,adj,nodes) for s in sorted(todo)]
        path=min(paths,key=len)
        for a,b in zip(path,path[1:]):tree[a].add(b);tree[b].add(a)
        nodes.update(path);todo-=nodes
    ops=[]
    def visit(v,parent):
        for c in sorted(tree[v]-{parent}):
            if c not in selected:ops.append((c,v))
            visit(c,v);ops.append((c,v))
    visit(q,None)
    return ops


def run(seed,helpers=True,ftweight=30,late_plus=False,release_weight=0):
    started=time.perf_counter();rng=random.Random(seed)
    cells=sorted(pc.CELLS+(pc.HELPERS if helpers else []));n=len(cells)
    adj={i:[j for j,b in enumerate(cells) if abs(a//6-b//6)+abs(a%6-b%6)==1]
         for i,a in enumerate(cells)}
    rows=[0 if late_plus and q==14 else pc.COLS[q] for q in cells]
    xs=[pc.fault_signature(q,'X',pc.HELPERS if helpers else []) for q in cells]
    zs=[pc.fault_signature(q,'Z',pc.HELPERS if helpers else []) for q in cells]
    if late_plus:xs[cells.index(14)]=zs[cells.index(14)]=0
    release_path=HERE.parents[2]/'work/lanes/NATIVE2_20261027/prefix_release.json'
    releases={int(k):v for k,v in json.loads(release_path.read_text())['release'].items()}
    active=set(range(n));path=[];totalbad=0;central_weight=(seed%4)*.75
    while len(active)>1:
        choices=[]
        for q in sorted(active):
            rest=active-{q};start=next(iter(rest))
            if len(bfs(start,rest,adj))!=len(rest):continue
            for trial in range(3):
                selected=expression(q,rows,active,adj,rng)
                ops=[] if selected is None or not selected else parity_tree(q,selected,active,adj)
                rr=list(rows);xx=list(xs);zz=list(zs);bad=0
                for a,b in ops:
                    bad+=int(not safe(xx[a]^xx[b]))+int(not safe(zz[a]^zz[b]))
                    rr[b]^=rr[a];xx[a]^=xx[b];zz[b]^=zz[a]
                assert selected is None or rr[q]==0
                degree=sum(a in active for a in adj[q])
                score=len(ops)+ftweight*bad+central_weight*degree
                release=releases[cells[q]]
                if selected is None:
                    score+=release_weight*max(0,release-20)*2
                else:
                    score-=release_weight*max(0,release-20)
                score+=.2*(sum(v!=0 for v in rr)-sum(v!=0 for v in rows))
                score+=rng.random()*2
                choices.append((score,q,rr,xx,zz,ops,bad))
        if not choices:raise RuntimeError('No removable graph vertex')
        _,q,rows,xs,zs,ops,bad=min(choices,key=lambda c:c[0])
        path+=ops;totalbad+=bad;active.remove(q)
    assert sum(v!=0 for v in rows)==11-int(late_plus)
    out=finish(cells,(tuple(rows),tuple(xs),tuple(zs)),path,1000+seed,False,time.perf_counter()-started,(14,) if late_plus else ())
    out['unsafe_cx_axis_checks']=totalbad;out['heuristic_fault_penalty']=ftweight
    out['method']='native parity-tree peeling'
    out['release_weight']=release_weight
    filename=HERE/'joint_resource'/f'peel_h{n-21}_r{10 if late_plus else 11}_rw{release_weight}_w{ftweight}_s{seed}.json'
    filename.write_text(json.dumps(out,indent=2)+'\n')
    print('PEEL',json.dumps({k:out[k] for k in ['cx','depth','unsafe_cx_axis_checks','seconds']}),flush=True)
    return out


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--start',type=int,default=0)
    ap.add_argument('--count',type=int,default=12);ap.add_argument('--ftweight',type=float,default=30)
    ap.add_argument('--no-helpers',action='store_true');ap.add_argument('--late-plus',action='store_true')
    ap.add_argument('--release-weight',type=float,default=0);a=ap.parse_args()
    for seed in range(a.start,a.start+a.count):run(seed,not a.no_helpers,a.ftweight,a.late_plus,a.release_weight)
