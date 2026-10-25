"""Exact per-index grid embeddability, including one nearest-neighbour move.
Moving one role splits its time-labelled vertex and inserts the move edge.
All positions are distinct; the destination is initially empty. A SWAP is
not one move of one role. Four-by-four suffices for the found witnesses;
a bipartite/degree obstruction is global, not restricted to this box.
"""
import json,itertools
from pathlib import Path
H=Path(__file__).resolve().parent

def embed(n,edges):
    adj={v:set() for v in range(n)}
    for a,b in edges:adj[a].add(b);adj[b].add(a)
    color={}
    for root in range(n):
        if root in color:continue
        color[root]=0;todo=[root]
        for a in todo:
            for b in adj[a]:
                if b in color:
                    if color[b]==color[a]:return None,'odd cycle'
                else:color[b]=1-color[a];todo.append(b)
    if any(len(xs)>4 for xs in adj.values()):return None,'degree > 4'
    near={q:[r for r in range(16) if abs(q//4-r//4)+abs(q%4-r%4)==1] for q in range(16)}
    found={}
    def go():
        if len(found)==n:return found.copy()
        v=max((v for v in adj if v not in found),key=lambda v:(sum(w in found for w in adj[v]),len(adj[v])))
        candidates=set(range(16))-set(found.values())
        for w in adj[v]:
            if w in found:candidates&=set(near[found[w]])
        for q in sorted(candidates):
            found[v]=q;r=go()
            if r:return r
            del found[v]
    return go(),'4x4 exhaustive'

rows=[]
for p in (H/'logs').glob('search_*.jsonl'):
    rows.extend(json.loads(l) for l in p.read_text().splitlines() if l)
seen=set();out=[]
for t in rows:
    key=json.dumps([t['n'],t['layers']])
    if key in seen:continue
    seen.add(key);edges={tuple(sorted(e)) for l in t['layers'] for e in l};p,why=embed(t['n'],edges);moves=[]
    if not p:
        for boundary in range(len(t['layers'])-1):
            for v in range(t['n']):
                ee={(v,t['n'])}
                for k,l in enumerate(t['layers']):
                    for a,b in l:
                        if k>boundary:a=t['n'] if a==v else a;b=t['n'] if b==v else b
                        ee.add(tuple(sorted((a,b))))
                pp,ww=embed(t['n']+1,ee)
                if pp:moves.append(dict(role=v,after_tick=boundary,positions=pp))
    cycle_rank=len(edges)-t['n']+1
    shape='tree' if cycle_rank==0 else 'square' if t['n']==4 and len(edges)==4 else 'square_leaf' if t['n']==5 and len(edges)==5 and p else 'other'
    out.append(dict(n=t['n'],layers=t['layers'],model_p2=t['second_order_p2'],shape=shape,edges=sorted(edges),static_positions=p,static_test=why,one_move=moves))
(H/'geometry.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(dict(graph_schedules=len(out),static=sum(bool(r['static_positions']) for r in out),one_move=sum(bool(r['one_move']) for r in out),competitive=[r for r in out if r['model_p2']<=26.7 and not r['static_positions']])),flush=True)
