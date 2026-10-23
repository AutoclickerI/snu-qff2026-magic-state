import json,sys
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/DR')
from synth import nbrs
B=[6,26,13,11,4,23,27]; C=[12,25,19,17,5,29,28]; H=[18,24,30,31,32,33,34,35]
ROWS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
def rank(vs):
    vs=list(vs);r=0
    while vs:
        p=max(vs)
        if p==0: break
        r+=1; vs=[min(v,v^p) for v in vs if v!=p]
        vs=[v for v in vs if v]
    return r
def verify(d):
    ops,piv=d["ops"],d["pivots"]
    allc=set(B+C+H)
    assert len(piv)==6 and len(set(piv))==6 and set(piv)<=allc
    val={q:0 for q in allc}
    for j,q in enumerate(piv): val[q]=1<<j
    for L in ops:
        used=set()
        for u,v in L:
            assert u in allc and v in allc and v in nbrs(u) and u not in used and v not in used
            used|={u,v}
        for u,v in L: val[v]^=val[u]
    assert all(val[q]==0 for q in H)
    # column vectors (over cells) of final state vs target
    cols=[sum(1<<q for q in allc if val[q]>>j&1) for j in range(6)]
    tg=[sum(1<<blk[i] for i in r) for blk in(B,C) for r in ROWS]
    return rank(cols)==6 and rank(cols+tg)==6
if __name__=="__main__":
    d=json.load(open(sys.argv[1])); print(verify(d), len(d["ops"]), sum(len(o) for o in d["ops"]))
