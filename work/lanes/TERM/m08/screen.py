"""M08 perfect-meter screen of all 2,825 stabilizer subgroups on the v36c incoming boundary table.

Input: <cut>.moments.json (all-orders Tr[acc g_m L]); reviewer 9's subspace list. For subgroup V (rows = generator
masks; bit i = generator i, i<3 X-type S_i, i>=3 Z-type S_{i-3}), a perfect meter accepts the syndrome sectors
orthogonal to V; then a terminal channel (per-qubit depolarizing tail) acts; the judge decodes all six ideally.
Tails: 'none'; 'idle' = D1(p) (the unavoidable last tick); 'class' = D1(2p/5) then D1(p) (last data CX with a measured
partner, then the last tick). Loss = n_V / A_V, all orders in the tail and exact (all orders) in the incoming table.
"""
import json, itertools, sys
import numpy as np
from pathlib import Path
cut=Path(sys.argv[1]); subs=json.load(open(sys.argv[2]))['syndrome_subspaces']['subspaces']
p=1e-3
M=json.load(open(cut.with_suffix('.moments.json')))
mom={(r['mask'],r['L']):r['value'] for r in M['moments']}
bX,bY=M['beta']['X'],M['beta']['Y']
pc=lambda v: bin(v).count('1')&1
sec={L:np.array([sum((-1)**pc(s&m)*mom[m,L] for m in range(64))/64 for s in range(64)]) for L in 'IXYZ'}
a,x,y=sec['I'],sec['X'],sec['Y']
sgnX=np.array([-1. if s&7 else 1. for s in range(64)]); sgnY=np.array([-1. if bool(s&7)^bool(s>>3&7) else 1. for s in range(64)])
SUP=({0,2,4,6},{1,2,5,6},{3,4,5,6})
col=[sum(((i in S)<<k) for k,S in enumerate(SUP)) for i in range(7)]   # syndrome column of qubit i (3 bits)
def synd(fx,fz):
    sx=0; sz=0
    for i in range(7):
        if fz>>i&1: sx^=col[i]
        if fx>>i&1: sz^=col[i]
    return sx|(sz<<3)
def kernels(q):
    """Kx(s), Ky(s): sum_F q_F sgn(s+f) (-1)^{comm(F,L)} for per-qubit D1(q)."""
    Kx=np.zeros(64); Ky=np.zeros(64)
    probs={0:1-q,1:q/3,2:q/3,3:q/3}   # per qubit: 0 I, 1 X, 2 Y, 3 Z  -> (x,z) bits
    xz={0:(0,0),1:(1,0),2:(1,1),3:(0,1)}
    for F in itertools.product(range(4),repeat=7):
        pr=1.0; fx=fz=0
        for i,f in enumerate(F):
            pr*=probs[f]; fx|=xz[f][0]<<i; fz|=xz[f][1]<<i
        f=synd(fx,fz); px=(-1)**pc(fz); py=(-1)**(pc(fx)+pc(fz))
        for s in range(64):
            Kx[s]+=pr*sgnX[s^f]*px; Ky[s]+=pr*sgnY[s^f]*py
    return Kx,Ky
def comp(a_,b_):  # depolarizing composition
    return 0.75*(1-(1-4*a_/3)*(1-4*b_/3))
tails={'none':None,'idle':p,'class':comp(2*p/5,p)}
K={}
for name,q in tails.items():
    K[name]=(sgnX,sgnY) if q is None else kernels(q)
def loss(acc_mask,tail):
    Kx,Ky=K[tail]
    A=a[acc_mask].sum(); n=((a-bX*Kx*x-bY*Ky*y)/2)[acc_mask].sum()
    return n/A, A
S=np.arange(64)
check=loss(np.ones(64,bool),'none')[0]
rows=[]
for sp in subs:
    R=sp['rref_rows']
    acc=np.array([all(pc(s&r)==0 for r in R) for s in S])
    rec=dict(dim=sp['dimension'],rows=R,
             gens=['*'.join(('X' if i<3 else 'Z')+str(i%3) for i in range(6) if r>>i&1) for r in R])
    for t in tails:
        L,A=loss(acc,t); rec[t]=float(L); rec['acc_'+t]=float(A/M['acceptance'])
    rows.append(rec)
full=next(r for r in rows if r['dim']==6)
out=dict(cut=str(cut),prior_acceptance=M['acceptance'],check_no_meter=dict(evaluator=M['loss_no_meter'],sectors=float(check)),
         sector_prob={int(s):float(a[s]/M['acceptance']) for s in np.argsort(-a)[:12]},
         full=full,tails=tails)
best={}
for d in range(7):
    rs=sorted([r for r in rows if r['dim']==d],key=lambda r:r['class'])
    best[d]=rs[:5]
out['best_by_dim']=best
out['n_below_full']={t:int(sum(r[t]<full[t]-1e-15 for r in rows if r['dim']<6)) for t in tails}
json.dump(dict(out,rows=rows),open(cut.with_name(cut.name+'.m08_screen.json'),'w'),indent=1)
print(json.dumps({k:v for k,v in out.items() if k!='best_by_dim'},indent=1))
for d in range(7):
    for r in best[d][:3]:
        print(d, r['gens'], 'none %.4e idle %.4e class %.4e acc_rel %.4f'%(r['none'],r['idle'],r['class'],r['acc_class']))
