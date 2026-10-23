import json,sys
B=[6,26,13,11,4,23,27]; C=[12,25,19,17,5,29,28]
ROWS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
def syn(e,blk):
    bits=[(q in e) for q in blk]
    return tuple(sum(bits[i] for i in r)%2 for r in ROWS), sum(bits)%2
def bad(e):
    sB,pB=syn(e,B); sC,pC=syn(e,C)
    zero=not any(sB)
    return sB==sC and pB==pC and pB==zero
def faults(d,cells=None):
    ops=d["ops"]; D=len(ops)
    cells=cells or sorted({q for L in ops for e in L for q in e}|set(B)|set(C)|set(d["pivots"]))
    out=[]
    for t in range(D+1):
        for q in cells:
            e={q}
            for L in ops[t:]:
                for u,v in L:
                    if u in e: e^={v}
            if bad(e): out.append((t,q,sorted(e)))
    return out
if __name__=="__main__":
    d=json.load(open(sys.argv[1])); f=faults(d); print(len(f),"bad faults"); print(f[:10])
