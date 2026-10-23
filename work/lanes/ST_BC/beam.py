import random, sys, json, time
B=[6,26,13,11,4,23,27]; C=[12,25,19,17,5,29,28]; H=[18,24,30,31,32,33,34,35]
ROWS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
cells=B+C+H
def nb(q):
    r,c=divmod(q,6)
    return [rr*6+cc for rr,cc in((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=rr<6 and 0<=cc<6]
S=set(cells)
edges=[(u,v) for u in cells for v in nb(u) if v in S]
def target():
    t={q:0 for q in cells}
    for blk,off in((B,0),(C,3)):
        for j,r in enumerate(ROWS):
            for i in r: t[blk[i]]|=1<<(j+off)
    return t
pc=[bin(i).count('1') for i in range(64)]
def h(st,W):
    nz=0;w=0
    for x in st.values():
        if x: nz+=1;w+=pc[x]
    return nz*W+w
def sample(st,rng,pz):
    used=set();ops=[]
    es=edges[:]; rng.shuffle(es)
    for u,v in es:
        if u in used or v in used: continue
        a,b=st[u],st[v]
        if a and a==b: p=0.95   # zeroing
        elif a and pc[a^b]<pc[b]: p=pz
        else: p=pz*0.3
        if rng.random()<p:
            used.add(u);used.add(v);ops.append((u,v))
    return ops
def apply(st,ops):
    s=dict(st)
    for u,v in ops: s[v]^=s[u]
    return s
def run(depth,beam,samples,seed,W=8,pz=0.4):
    rng=random.Random(seed)
    cur=[(h(target(),W),target(),[])]
    for d in range(depth):
        cand={}
        for _,st,hist in cur:
            for _ in range(samples):
                ops=sample(st,rng,pz)
                if not ops: continue
                ns=apply(st,ops)
                key=tuple(ns[q] for q in cells)
                if key in cand: continue
                cand[key]=(h(ns,W)+rng.random()*0.5,ns,hist+[ops])
        cur=sorted(cand.values(),key=lambda x:x[0])[:beam]
        best=cur[0]
        nz=sum(1 for x in best[1].values() if x)
        print(d,best[0],nz,flush=True)
        for sc,st,hist in cur:
            if sum(1 for x in st.values() if x)==6:
                return hist,st
    return None,None
if __name__=="__main__":
    depth,beam,samples,seed=map(int,sys.argv[1:5])
    hist,st=run(depth,beam,samples,seed)
    if hist:
        piv=[q for q,x in st.items() if x]
        fw=[ops for ops in reversed(hist)]
        n=sum(len(o) for o in fw)
        print("FOUND",len(fw),n)
        json.dump({"ops":[[list(e) for e in o] for o in fw],"pivots":piv},open(f"sol_{depth}_{seed}.json","w"))
