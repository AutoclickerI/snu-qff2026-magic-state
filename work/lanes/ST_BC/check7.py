import json,sys
from check import *
def verify7(d):
    ops,piv=d["ops"],d["pivots"]; allc=set(B+C+H)
    val={q:0 for q in allc}
    for j,q in enumerate(piv): val[q]=1<<j
    for L in ops:
        used=set()
        for u,v in L:
            assert v in nbrs(u) and u not in used and v not in used and u in allc and v in allc; used|={u,v}
        for u,v in L: val[v]^=val[u]
    cols=[sum(1<<q for q in B+C if val[q]>>j&1) for j in range(6)]
    tg=[sum(1<<blk[i] for i in r) for blk in(B,C) for r in ROWS]
    return rank(cols)==6 and rank(cols+tg)==6
if __name__=="__main__": print(verify7(json.load(open(sys.argv[1]))))
