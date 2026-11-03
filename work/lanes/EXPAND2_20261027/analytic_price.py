"""Sparse analytic sign kernels for commuting pi/8 circuits.

Lane-local extension: leaves qtools and judge sources untouched. It avoids the
2**T dense table by conjugating each measured Pauli through commuting rotations
and solving the binary X-support equation for the surviving terms. The resulting
Walsh coefficients feed the existing all-orders channel contraction unchanged.
"""
import os
for _key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):
    os.environ[_key]='1'
import argparse, hashlib, json, math, re, sys, time
from pathlib import Path
from collections import defaultdict
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'work/tools'))
from qtools.evaluator import frontend as f, sparse_walsh as sw
from qtools.validity import raw_check
from qtools.version import EVALUATOR_VERSION


def solve_x(columns,target):
    """Particular subset and independent null subsets; None if inconsistent."""
    piv={};null=[]
    for j,col in enumerate(columns):
        v=col;mask=1<<j
        while v:
            h=v.bit_length()-1
            if h not in piv:
                piv[h]=(v,mask);break
            a,b=piv[h];v^=a;mask^=b
        if not v:null.append(mask)
    ans=0
    while target:
        h=target.bit_length()-1
        if h not in piv:return None
        v,mask=piv[h];target^=v;ans^=mask
    return ans,null


def kernel(eng,active,key):
    """Return the same unnormalized Walsh coefficients as sw.sparse_kernel."""
    nr=len(eng.rot);na=len(active)
    if nr+na>63:raise ValueError('selector masks require at most63 bits')
    q=(0,0,1) if key is None else eng.Qs[key]
    states=[];weights=[]
    rotations=[r[:3] for r in eng.rot]
    for u in range(1<<na):
        p=q
        for j,i in enumerate(active):
            if u>>j&1:p=f.mul(p,eng.projs[i])
        js=[j for j,r in enumerate(rotations) if f.comm(r,p)]
        found=solve_x([rotations[j][0] for j in js],p[0])
        if found is None:continue
        first,null=found
        if len(null)>18:
            raise MemoryError(f'kernel moment {key}, parity {u} needs 2**{len(null)} selector terms; use a factored kernel or official sampling')
        cosprod=math.prod(math.cos(2*eng.rot[j][3]) for j in js)
        signs=sum((1<<i) for i,j in enumerate(js) if math.sin(2*eng.rot[j][3])<0)
        def product(mask):
            pp=(0,0,1);global_mask=0
            while mask:
                b=mask&-mask;mask^=b;j=js[b.bit_length()-1]
                pp=f.mul(pp,rotations[j]);global_mask^=1<<j
            return pp,global_mask
        base,gmask=product(first)
        pp=f.mul(p,base)
        assert pp[0]==0
        scalar=pp[2]
        deltas=[]
        for mask in null:
            pn,gn=product(mask)
            assert pn[0]==0 and abs(pn[2].imag if isinstance(pn[2],complex) else 0)<1e-9
            deltas.append((mask,gn,pn[2]))
        mask=first;previous=0
        for n in range(1<<len(null)):
            gray=n^(n>>1)
            if n:
                b=gray^previous;dm,dg,dc=deltas[b.bit_length()-1]
                mask^=dm;gmask^=dg;scalar*=dc
            previous=gray
            value=scalar*(1j**(mask.bit_count()%4))*((-1)**((mask&signs).bit_count()%2))*cosprod
            if abs(complex(value).imag)>1e-9:
                raise ArithmeticError(('imaginary diagonal moment',key,u,mask,value))
            v=float(complex(value).real)
            if v:
                states.append(u|(gmask<<na));weights.append((1<<nr)*v)
    order=np.argsort(np.asarray(states,dtype=np.uint64))
    return np.asarray(states,dtype=np.uint64)[order],np.asarray(weights,dtype=float)[order],0.


def prepare(stem):
    stem=Path(stem).resolve();text=stem.with_suffix('.qasm').read_text()
    data=json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    if re.search(r'//\s*(FRAME_[XZ]|POSTSELECT)\b',text):
        raise ValueError('zero-frame/no-POSTSELECT only')
    used=set()
    for line in text.splitlines():
        if not line.lstrip().startswith(('barrier','qreg','//')):
            used.update(map(int,re.findall(r'q\[(\d+)\]',line)))
    for line in text.splitlines():
        if line.lstrip().startswith('barrier'):
            assert used.issubset(set(map(int,re.findall(r'q\[(\d+)\]',line))))
    raw=raw_check(text,data)
    if not raw['ok']:raise ValueError(raw)
    ops,dets=f.parse_current(text);f.DATA=list(data)
    original=f.noise_blocks
    try:
        f.noise_blocks=lambda text,p,first_order=True:original(text,p,first_order=False)
        m=f.make_model(ops,dets)
    finally:f.noise_blocks=original
    eng=f.Engine(m)
    changes=sw.canonicalize_detector_rows(m,eng)
    if changes:eng=f.Engine(m)
    assert all(p[0]==0 for p in eng.projs)
    assert all(v==0 for v in eng.v)
    assert all(not f.comm(a[:3],b[:3]) for i,a in enumerate(eng.rot) for b in eng.rot[i+1:])
    assert all(abs(abs(t)-math.pi/8)<1e-12 for x,z,c,t in eng.rot)
    assert all(not f.comm(q,p) for q in eng.Qs.values() for p in eng.projs)
    A0,N0=eng.ntable(0,0)
    assert abs(A0-1)<1e-10 and abs(N0[0])<1e-10
    active=[i for i,p in enumerate(eng.projs) if p[:2]!=(0,0)]
    nd=len(dets);ks=tuple(active+list(range(nd,nd+len(eng.rot))))
    groups=defaultdict(list)
    for fault in m.faults:groups[fault['chan']].append(fault)
    return text,data,raw,m,eng,groups,nd,ks,active


def price(stem,verbose=False):
    started=time.perf_counter()
    text,data,raw,m,eng,groups,nd,ks,active=prepare(stem)
    compiled,elim=sw.compile_best(m,eng,groups,nd,ks,save=False)
    values=[];max_states=0
    try:
        for key in [None]+eng.keys:
            states,weights,_=kernel(eng,active,key)
            vec,peak=sw.contract_quotient(compiled,states,0 if key is None else sw.emask_for(key),elim['order'])
            values.append(float(np.dot(weights,vec)/(1<<len(ks))))
            max_states=max(max_states,len(states))
            if verbose:print('moment',key,len(states),values[-1],flush=True)
    finally:sw.COLUMNS.clear()
    A=values[0];obs=sum(w*b*v for w,b,v in zip(eng.W,eng.beta,values[1:]))
    return dict(loss=float((A-obs)/(2*A)),acceptance=A,raw=raw,width=elim['width'],
                basis=elim['basis'],max_kernel_states=max_states,rotations=len(eng.rot),
                rank_rot=eng.rank_rot,qasm_sha256=hashlib.sha256(text.encode()).hexdigest(),
                evaluator='analytic commuting-Pauli kernel plus pinned qtools contraction',
                evaluator_version=EVALUATOR_VERSION,data_qubits=data,seconds=time.perf_counter()-started)


def compare(stem):
    """Compare every moment kernel against independent dense construction."""
    m,e,groups,nd,ks,psi,where,_=sw.prepare(Path(stem),True)
    active=[i for i,p in enumerate(e.projs) if p[:2]!=(0,0)]
    worst=0.;count=0
    for key in [None]+e.keys:
        s,w,_=sw.sparse_kernel(e,ks,psi,where,key)
        sa,wa,_=kernel(e,active,key)
        d=dict(zip(map(int,s),w));da=dict(zip(map(int,sa),wa))
        err=sum(abs(d.get(k,0.)-da.get(k,0.)) for k in d.keys()|da.keys())/(1<<len(ks))
        worst=max(worst,err);count+=1
        assert err<1e-11,(key,err,len(d),len(da))
    return dict(stem=str(stem),moments=count,max_normalized_kernel_l1_difference=worst)


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--compare',action='store_true');ap.add_argument('--verbose',action='store_true')
    args=ap.parse_args()
    result=compare(Path(args.stem)) if args.compare else price(Path(args.stem),args.verbose)
    print(json.dumps(result,indent=2),flush=True)
