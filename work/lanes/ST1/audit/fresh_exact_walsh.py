"""Exact finite-p independent-Pauli signature contraction on v22 (prototype)."""
import sys,json,math,time
from pathlib import Path
from collections import defaultdict
import numpy as np
import full_single_audit as fa
from fresh_signature_width import parse_current,minfill,STEM,ROOT

def fwht(a):
    a=a.copy();n=a.size;h=1
    while h<n:
        t=a.reshape(-1,2*h);l=t[:,:h].copy();r=t[:,h:].copy()
        t[:,:h]=l+r;t[:,h:]=l-r;h*=2
    return a

def prepare(stem=STEM):
    fa.DATA=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    ops,dets=parse_current(stem.with_suffix('.qasm').read_text())
    old=fa.noise_blocks
    fa.noise_blocks=lambda text,p,first_order=True:old(text,p,first_order=False)
    m=fa.make_model(ops,dets);fa.noise_blocks=old
    eng=fa.Engine(m);nd=len(dets);nr=len(m.rots)
    groups=defaultdict(list)
    for f in m.faults:groups[f['chan']].append(f)
    active=[i for i,p in enumerate(eng.projs) if p[:2]!=(0,0)]
    assert all(p[0]==0 for p in eng.projs)
    assert all(v==0 for v in eng.v)
    kernel_scope=tuple(active+list(range(nd,nd+nr)))
    assert len(active)==4 and nr==15
    states=np.arange(1<<nr,dtype=np.uint32)
    psi=np.zeros((len(states),eng.N),dtype=np.complex128);psi[:,0]=1
    for j,(mj,wj,coef,theta) in enumerate(eng.rot):
        signs=1-2*((states>>j)&1).astype(np.int8)
        psi=np.cos(theta)*psi+(1j*math.sin(theta)*coef)*signs[:,None]*(psi*eng.sgn(wj)[None,:])[:,eng.idx.astype(int)^mj]
    dvals=np.zeros(eng.N,dtype=np.int32)
    for j,i in enumerate(active):dvals|=np.bitwise_count(np.arange(eng.N)&eng.projs[i][1])%2<<j
    where=[np.flatnonzero(dvals==v) for v in range(1<<len(active))]
    assert all(len(v)==2 for v in where)
    scopes=[]
    for fs in groups.values():
        union=0
        for f in fs:union|=f['d']|(f['s']<<nd)
        scopes.append({i for i in range(union.bit_length()) if union>>i&1})
    scopes.append(set(kernel_scope));elim=minfill(scopes)
    return m,eng,groups,nd,kernel_scope,psi,where,elim

def kernel(eng,kernel_scope,psi,where,key):
    if key is None:raw=(psi.conj()*psi).real
    else:
        mj,wj,c=eng.Qs[key]
        raw=(psi[:,eng.idx.astype(int)^mj].conj()*c*eng.sgn(wj)[None,:]*psi).real
    g=np.stack([raw[:,idx].sum(axis=1) for idx in where],axis=1)
    vals=fwht(g.reshape(-1))
    vals[np.abs(vals)<1e-12]=0
    return (kernel_scope,vals.reshape((2,)*len(kernel_scope),order='F'))

def channel_factor(m,fs,nd,emask):
    coeff=defaultdict(float)
    coeff[0]=1-m.chans[fs[0]['chan']]['p']
    for f in fs:
        sig=f['d']|(f['s']<<nd)
        coeff[sig]+=f['p']*(-1 if (f['e']&emask).bit_count()%2 else 1)
    coeff={k:v for k,v in coeff.items() if abs(v)>1e-18}
    union=0
    for sig in coeff:union|=sig
    scope=tuple(i for i in range(union.bit_length()) if union>>i&1)
    ix=np.arange(1<<len(scope),dtype=np.uint32);val=np.zeros(len(ix))
    for sig,p in coeff.items():
        sub=sum(((sig>>q)&1)<<j for j,q in enumerate(scope))
        val+=p*(1-2*(np.bitwise_count(ix&sub)%2).astype(np.int8))
    return scope,val.reshape((2,)*len(scope),order='F')

def contract(factors,order):
    for v in order:
        bucket=[f for f in factors if v in f[0]]
        factors=[f for f in factors if v not in f[0]]
        if not bucket:continue
        union=tuple(sorted(set().union(*(set(s) for s,a in bucket))))
        out=np.ones((2,)*len(union))
        for scope,a in bucket:
            out*=a.reshape(tuple(2 if u in scope else 1 for u in union))
        out=out.mean(axis=union.index(v))
        factors.append((tuple(q for q in union if q!=v),out))
    assert all(not s for s,a in factors)
    return math.prod(float(a) for s,a in factors)

def emask_for(key):
    T,a,b=key
    return a|(b<<3)|(1<<6)|((1<<8) if T=='X' else (1<<7)|(1<<9))

if __name__=='__main__':
    stem=Path(sys.argv[2]) if len(sys.argv)>2 else STEM
    t=time.perf_counter();m,eng,groups,nd,ks,psi,where,elim=prepare(stem)
    nkeys=int(sys.argv[1]) if len(sys.argv)>1 else 0
    keys=[None]+eng.keys[:nkeys]
    results=[]
    for key in keys:
        start=time.perf_counter();emask=0 if key is None else emask_for(key)
        factors=[channel_factor(m,fs,nd,emask) for fs in groups.values()]
        kn=kernel(eng,ks,psi,where,key);nz=int(np.count_nonzero(kn[1]));factors.append(kn)
        val=contract(factors,elim['order'])
        r=dict(key=key,value=val,seconds=time.perf_counter()-start,kernel_nonzero=nz)
        results.append(r);print(json.dumps(r),flush=True)
    out=dict(source=str(stem),channels=len(m.chans),components=len(m.faults),width=elim['width'],results=results,seconds=time.perf_counter()-t)
    if nkeys>=len(eng.keys):
        A=results[0]['value'];obs=sum(w*b*r['value'] for w,b,r in zip(eng.W,eng.beta,results[1:]));out['acceptance']=A;out['loss']=(A-obs)/(2*A)
        print(json.dumps({k:v for k,v in out.items() if k!='results'}),flush=True)
    (ROOT/('audit/fresh_exact_walsh_'+stem.name+'_result.json')).write_text(json.dumps(out,indent=2))
