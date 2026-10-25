"""Finite partial-coherence resource certificates and optimistic logical-frame screen.

The C-family identities are exact finite-support identities.  The frame calculation
uses the pinned v36c boundary table; it is an oracle, not a realizable free meter.
"""
import itertools, json, math
from pathlib import Path
import numpy as np

HERE=Path(__file__).resolve().parent
def span(gs):
    s={0}
    for g in gs: s|={u^g for u in tuple(s)}
    return tuple(sorted(s))
def subspaces(n):
    seen={(0,)}; frontier={(0,)}
    while frontier:
        new=set()
        for s in frontier:
            for v in range(1,1<<n):
                if v not in s:
                    t=tuple(sorted(set(s)|{u^v for u in s}))
                    if t not in seen: new.add(t)
        seen|=new; frontier=new
    return sorted(seen,key=lambda s:(len(s),s))
def basis(s):
    b=[]; t={0}
    for v in s:
        if v not in t: b.append(v);t|={u^v for u in tuple(t)}
    return b
def pc(v):return v.bit_count()&1

GEN=(0b1010101,0b1100110,0b1111000)
def lift(v):
    out=0
    for i,g in enumerate(GEN):
        if v>>i&1:out^=g
    return out
C=span(GEN)
rows=[]
for w in subspaces(3):
    v=tuple(sorted(lift(t) for t in w));r=(len(v)).bit_length()-1
    support={(u,u^t) for u in C for t in v}
    post={(b,c^b) for b,c in support}
    target={(b,c) for b in C for c in v}
    assert post==target and len(support)==2**(3+r)
    psi=np.zeros((128,128))
    for b,c in support:psi[b,c]=1/math.sqrt(len(support))
    evals=np.linalg.eigvalsh(psi@psi.T)
    nz=evals[evals>1e-10]
    assert len(nz)==2**(3-r)
    assert np.max(np.abs(nz-2**-(3-r)))<1e-12
    vp=tuple(z for z in range(128) if all(not pc(z&t) for t in v))
    assert len(basis(v))+len(basis(vp))==7
    rows.append(dict(r=r,V_basis=basis(v),V_words=v,
                     C_X_stabilizers=basis(v),C_Z_stabilizers=basis(vp),
                     initial_plus_count=3+r,schmidt_rank=len(nz),
                     schmidt_weights=nz.tolist(),support_identity=True))
assert len(rows)==16 and sum(x['r'] in (1,2) for x in rows)==14
loss_pair=((.5,.5,0),(.5,.5,1),(0,1,1))
base_rates=((11,7,7),(11,7,7),(10,7,7),(15,7,7),(11,7,7),(11,7,7),(15,7,7))
def terminal_cost(rs):
    return sum(rs[i][a]*rs[j][b]*loss_pair[a][b]
               for i,j in itertools.combinations(range(7),2)
               for a in range(3) for b in range(3))/225
base_terminal=terminal_cost(base_rates)
for rec in rows:
    cover=0
    for g in rec['V_basis']: cover|=g
    rr=[list(v) for v in base_rates]
    for i in range(7):
        if cover>>i&1: rr[i][0]-=1
    rec['single_Z_C_detected_indices']=[i for i in range(7) if cover>>i&1]
    rec['all_single_X_C_detected']=all((1<<i) not in rec['V_words'] for i in range(7))
    rec['ideal_C_readout_terminal_second_order_p2']=terminal_cost(rr)
    rec['ideal_C_readout_terminal_gain_at_p001']=(base_terminal-terminal_cost(rr))*1e-6
json.dump(dict(source_pin='0ff9423a8e69c13998ab1baf7bf09c8e97558a60',
               contract='CX_BC |R_V> = |0_L>_B |V>_C',rows=rows,
               terminal_model_reference_second_order_p2=base_terminal,
               terminal_model_caveat='Ideal C stabilizer meter, unchanged v36c terminal data rates; no resource/readout noise or geometric cost. Partial-C state preparation has not been implemented.'),
          open(HERE/'partial_coherence_contracts.json','w'),indent=2)

M=json.load(open(HERE/'source/work/lanes/TERM/m08/v36c_b43.moments.json'))
mom={(r['mask'],r['L']):r['value'] for r in M['moments']}
W=np.array([[(-1)**pc(s&m) for m in range(64)] for s in range(64)],float)
sec={L:W@np.array([mom[m,L] for m in range(64)])/64 for L in 'IXYZ'}
a,x,y=sec['I'],sec['X'],sec['Y'];bx,by=M['beta']['X'],M['beta']['Y']
sx=np.array([-1. if s&7 else 1. for s in range(64)])
sy=np.array([-1. if bool(s&7)^bool(s>>3&7) else 1. for s in range(64)])
cols=[sum(((g>>i&1)<<k) for k,g in enumerate(GEN)) for i in range(7)]
S=np.arange(64)
def kernels(q):
    kx=np.zeros(64);ky=np.zeros(64)
    for f in itertools.product(range(4),repeat=7):
        pr=1.;s=zx=zy=0
        for i,t in enumerate(f):
            pr*=1-q if t==0 else q/3
            isx=t in (1,2);isz=t in (2,3)
            if isz:s^=cols[i];zx^=1
            if isx:s^=cols[i]<<3
            zy^=isx^isz
        kx+=pr*((-1)**zx)*sx[S^s]
        ky+=pr*((-1)**zy)*sy[S^s]
    return kx,ky
p=.001;tails={'none':0.,'idle':p,'class':.75*(1-(1-4*p/3)*(1-4*(2*p/5)/3))}
spaces=subspaces(6);assert len(spaces)==2825
out={'source':'pinned v36c_b43 table, not current v36g',
     'warning':'Optimistic incoming-syndrome FRAME oracle. No physical access or meter cost charged.',
     'tails':tails,'rows':[]}
for tail,q in tails.items():
    kx,ky=(sx,sy) if not q else kernels(q)
    vx=bx*kx*x;vy=by*ky*y
    rr=[]
    for u in spaces: # accepted syndrome subspace; orthogonal extraction rank = 6-dim(u)
        ii=np.array(u);A=a[ii].sum()
        plain=(A-vx[ii].sum()-vy[ii].sum())/(2*A)
        oracle=(A-np.abs(vx[ii]).sum()-np.abs(vy[ii]).sum())/(2*A)
        fX=W[:,ii]@vx[ii];fY=W[:,ii]@vy[ii]
        lx=int(np.argmax(fX));ly=int(np.argmax(fY))
        lin=(A-fX[lx]-fY[ly])/(2*A)
        rr.append(dict(extraction_rank=6-(len(u).bit_length()-1),accepted=basis(u),
                       acceptance=A,plain_loss=plain,oracle_loss=oracle,linear_frame_loss=lin,
                       frame_Z_mask=lx,frame_X_mask=lx^ly))
    full=rr[0]
    best=sorted(rr[1:],key=lambda r:r['linear_frame_loss'])[:10]
    entry=dict(tail=tail,full=full,best_proper=best,
               n_oracle_wins=sum(r['oracle_loss']<full['plain_loss']-1e-15 for r in rr[1:]),
               n_linear_wins=sum(r['linear_frame_loss']<full['plain_loss']-1e-15 for r in rr[1:]))
    out['rows'].append(entry)
    print(tail,'full',full,'best',best[0], 'oracle wins',entry['n_oracle_wins'],flush=True)
json.dump(out,open(HERE/'optimistic_frame_screen.json','w'),indent=2,
          default=lambda t:t.item() if isinstance(t,np.generic) else t)
