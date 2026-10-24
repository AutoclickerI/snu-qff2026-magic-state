"""All 256 data Pauli moments Tr[acc * g_m * L] at a cut (g_m: product of the six Steane generators selected by
mask m, L in {I, X7, Y7, Z7}), all orders, with the MAIN sparse cutset contraction (work/lanes/MAIN/sparse).
Usage: boundary_moments.py <stem> [procs]  ->  <stem>.moments.json
"""
import sys, json, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent.parent/'MAIN'/'sparse'))
import numpy as np
import sparse_walsh as sw
import frontend as fa
stem=Path(sys.argv[1]).resolve(); procs=int(sys.argv[2]) if len(sys.argv)>2 else 1
m,eng,groups,nd,ks,psi,where,_=sw.prepare(stem,canonicalize=True)
compiled,elim=sw.compile_best(m,eng,groups,nd,ks)
QX=m.Q[('X',0,0)]; QY=m.Q[('Y',0,0)]
xz=fa.mul(QX,QY); QZ=(xz[0],xz[1],xz[2]*1j)
Ls={'I':(0,0,1),'X':QX,'Y':QY,'Z':QZ}
lbits={'I':0,'X':1<<6,'Y':(1<<6)|(1<<7),'Z':1<<7}
keys=[]
for mask in range(64):
    g=(0,0,1)
    for i in range(6):
        if mask>>i&1: g=fa.mul(g,m.gen_m[i])
    for L in 'IXYZ':
        P=fa.mul(g,Ls[L])
        x=eng.B.express(P[0]); assert x is not None, (mask,L)
        k=('M',mask,L); eng.Qs[k]=(x,eng._w(P[1]),P[2]); keys.append(k)
def row(key):
    t=time.perf_counter()
    states,weights,om=sw.sparse_kernel(eng,ks,psi,where,key)
    em=key[1]|lbits[key[2]]
    if len(states)==0:
        return dict(mask=key[1],L=key[2],value=0.0,omission=om,seconds=time.perf_counter()-t)
    f=sw.factors_for(compiled,states,em)
    vec,_=sw.contract_selector(f,elim['order'],len(states))
    return dict(mask=key[1],L=key[2],value=float(np.dot(weights,vec)/(1<<len(ks))),omission=om,seconds=time.perf_counter()-t)
# reference: the evaluator's own acceptance and loss for this cut, to validate the sector algebra later
def ref(key):
    return sw._row(key)
sw._CTX.update(eng=eng,ks=ks,psi=psi,where=where,compiled=compiled,elim=elim)
t0=time.perf_counter()
if procs>1:
    import multiprocessing as mp
    with mp.get_context('fork').Pool(procs) as pool:
        rows=list(pool.imap(row,keys)); refs=list(pool.imap(ref,[None]+eng.keys))
else:
    rows=[row(k) for k in keys]; refs=[ref(k) for k in [None]+eng.keys]
A=refs[0]['value']; obs=sum(w*b*r['value'] for w,b,r in zip(eng.W,eng.beta,refs[1:]))
out=dict(source=str(stem),channels=len(m.chans),A0=eng.A0,beta={'X':float(eng.beta[[k[0] for k in eng.keys].index('X')]),
         'Y':float(eng.beta[[k[0] for k in eng.keys].index('Y')])},acceptance=A,loss_no_meter=(A-obs)/(2*A),
         moments=rows,seconds=time.perf_counter()-t0)
stem.with_suffix('.moments.json').write_text(json.dumps(out,indent=1)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='moments'}))
