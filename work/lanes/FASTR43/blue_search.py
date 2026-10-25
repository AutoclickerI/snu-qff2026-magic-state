import numpy as np, itertools
Q={0:0,1:1,2:2,3:3,7:4,8:5}; n=6
def cx(c,t):
    M=np.eye(2*n,dtype=np.uint8); c,t=Q[c],Q[t]; M[t,c]=1; M[n+c,n+t]=1; return M
def seq(gs):
    M=np.eye(2*n,dtype=np.uint8)
    for g in gs: M=(cx(*g)@M)%2
    return M
# original per tick (q1 and q2 ops), ticks 29..34
orig_t={29:[(2,1)],30:[(3,2),(7,1)],31:[(8,2),(0,1)],32:[(2,8),(1,0)],33:[(2,3),(1,7)],34:[(2,1)]}
O=seq([g for t in sorted(orig_t) for g in orig_t[t]])
q1fixed={30:(7,1),31:(0,1),32:(1,0),33:(1,7)}
choices=[None,(8,2),(2,8),(3,2),(2,3),(2,1),(1,2)]
found=0
for s in itertools.product(choices,repeat=6):
    ticks=list(range(29,35))
    # q8 gates must be at <=31
    if any(g and 8 in g and t>31 for g,t in zip(s,ticks)):continue
    gs=[]; ok=True
    for g,t in zip(s,ticks):
        if g: 
            if 1 in g and t in q1fixed: ok=False;break
            gs.append(g)
        if t in q1fixed: gs.append(q1fixed[t])
    if not ok: continue
    if (seq(gs)==O).all(): print('match',s); found+=1
print('found',found)
