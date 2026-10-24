"""Sparse Fourier-kernel cutset contraction of the reviewer Walsh model.

Nonzero kernel assignments become a selector axis. All remaining detector
variables are summed exactly; no Monte Carlo or fault-order truncation.
The upstream kernel's numerical zero threshold is separately reported.
"""
import json, math, sys, time
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent
import frontend as fa
from frontend import parse_current
def minfill(scopes):
    graph=defaultdict(set)
    for ss in scopes:
        for v in ss:graph[v].update(ss-{v})
    width=0;cost=0;order=[];sizes=[]
    while graph:
        def key(v):
            n=graph[v];fill=sum(len(n-{u}-graph[u]) for u in n)//2
            return fill,len(n),v
        v=min(graph,key=key);n=graph.pop(v);width=max(width,len(n));cost+=2**len(n)
        order.append(v);sizes.append(len(n))
        for u in n:graph[u].discard(v);graph[u].update(n-{u})
    return dict(width=width,work_entries=cost,order=order,bucket_sizes=sizes)

def fwht(a):
    a=a.copy();n=a.size;h=1
    while h<n:
        t=a.reshape(-1,2*h);l=t[:,:h].copy();r=t[:,h:].copy()
        t[:,:h]=l+r;t[:,h:]=l-r;h*=2
    return a

def emask_for(key):
    T,a,b=key
    return a|(b<<3)|(1<<6)|((1<<8) if T=='X' else (1<<7)|(1<<9))

def canonicalize_detector_rows(m,eng):
    """Replace dependent reduced projectors by identity using invertible row XOR.

    The identity projector still enforces a detector-fault parity. No detector
    constraint or fault information is discarded.
    """
    basis={}
    changes={}
    original=list(m.proj_m)
    for i,(x,w,c) in enumerate(eng.projs):
        assert x==0 and abs(c-1)<1e-10
        if not w: continue
        v,mask=w,1<<i
        while v:
            lead=v.bit_length()-1
            if lead not in basis:
                basis[lead]=(v,mask)
                break
            bv,bmask=basis[lead]
            v^=bv;mask^=bmask
        if not v:
            changes[i]=mask
    for i,mask in changes.items():
        p=(0,0,1)
        for j in range(len(original)):
            if mask>>j&1:p=fa.mul(p,original[j])
        m.proj_m[i]=p
    for f in m.faults:
        d=f['d'];new=d
        for i,mask in changes.items():
            new=(new&~(1<<i))|(((d&mask).bit_count()%2)<<i)
        f['d']=new
    return changes

def prepare(stem,canonicalize=False):
    text = stem.with_suffix('.qasm').read_text()
    import re
    used=set()
    for line in text.splitlines():
        if not line.lstrip().startswith(('barrier','qreg','//')):
            used.update(map(int,re.findall(r'q\[(\d+)\]',line)))
    for line in text.splitlines():
        if line.lstrip().startswith('barrier') and not used.issubset(set(map(int,re.findall(r'q\[(\d+)\]',line)))):
            raise ValueError('Prototype requires every barrier to cover all used qubits')
    # This prototype reuses the independently validated integer-Pauli frontend.
    # Logical parity/constant frames are supported; POSTSELECT is out of scope.
    if '// POSTSELECT' in text:
        raise ValueError('Prototype does not support explicit POSTSELECT')
    fa.FRAME_X=[]; fa.FRAME_Z=[]; fa.FRAME_X_CONST=0; fa.FRAME_Z_CONST=0
    for line in text.splitlines():
        if line.startswith('// FRAME_X'):
            fa.FRAME_X=list(map(int,re.findall(r'c\[(\d+)\]',line)))
            cc=re.search(r'FRAME_X\(([01])\)',line);fa.FRAME_X_CONST=int(cc.group(1)) if cc else 0
        if line.startswith('// FRAME_Z'):
            fa.FRAME_Z=list(map(int,re.findall(r'c\[(\d+)\]',line)))
            cc=re.search(r'FRAME_Z\(([01])\)',line);fa.FRAME_Z_CONST=int(cc.group(1)) if cc else 0
    fa.DATA = json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    ops, dets = parse_current(text)
    previous = fa.noise_blocks
    fa.noise_blocks = lambda text,p,first_order=True: previous(text,p,first_order=False)
    try:
        m = fa.make_model(ops,dets)
    finally:
        fa.noise_blocks = previous
    eng = fa.Engine(m)
    changes=canonicalize_detector_rows(m,eng) if canonicalize else {}
    if changes: eng=fa.Engine(m)
    m.detector_row_changes=changes
    nd, nr = len(dets), len(m.rots)
    active = [i for i,p in enumerate(eng.projs) if p[:2] != (0,0)]
    assert all(p[0] == 0 for p in eng.projs), 'non-diagonal accepted kernel needs a generalized kernel'
    assert all(v == 0 for v in eng.v), 'nonzero references unsupported by this prototype'
    assert nr <= 20, 'dense sign-kernel construction limit'
    A0, N0 = eng.ntable(0,0)
    assert A0 > 1-1e-10 and abs(N0[0]) < 1e-10, (A0,N0[0])
    ks = tuple(active + list(range(nd,nd+nr)))
    states = np.arange(1<<nr,dtype=np.uint32)
    psi = np.zeros((len(states),eng.N),dtype=np.complex128)
    psi[:,0] = 1
    for j,(mj,wj,coef,theta) in enumerate(eng.rot):
        signs = 1-2*((states>>j)&1).astype(np.int8)
        psi = np.cos(theta)*psi + (1j*math.sin(theta)*coef)*signs[:,None]*(psi*eng.sgn(wj)[None,:])[:,eng.idx.astype(int)^mj]
    dvals = np.zeros(eng.N,dtype=np.int32)
    for j,i in enumerate(active):
        dvals |= (np.bitwise_count(np.arange(eng.N)&eng.projs[i][1])%2)<<j
    where = [np.flatnonzero(dvals==v) for v in range(1<<len(active))]
    groups = defaultdict(list)
    for f in m.faults: groups[f['chan']].append(f)
    scopes=[]
    for fs in groups.values():
        union=0
        for f in fs: union |= f['d'] | (f['s']<<nd)
        scopes.append({i for i in range(union.bit_length()) if union>>i&1})
    scopes.append(set(ks))
    return m,eng,groups,nd,ks,psi,where,minfill(scopes)

def sparse_kernel(eng,ks,psi,where,key,threshold=1e-12):
    if key is None:
        raw=(psi.conj()*psi).real
    else:
        mj,wj,c=eng.Qs[key]
        raw=(psi[:,eng.idx.astype(int)^mj].conj()*c*eng.sgn(wj)[None,:]*psi).real
    g=np.stack([raw[:,idx].sum(axis=1) for idx in where],axis=1)
    flat=fwht(g.reshape(-1))
    small=np.abs(flat)<threshold
    # Each remaining normalized characteristic-factor contraction is bounded
    # by one in magnitude. This bounds omission error, not floating arithmetic.
    omission_bound=float(np.abs(flat[small]).sum()/(1<<len(ks)))
    states=np.flatnonzero(~small).astype(np.uint32)
    return states,flat[states],omission_bound

def compile_channels(m, groups, nd, kernel_scope):
    kmap = {q: j for j, q in enumerate(kernel_scope)}
    compiled = []
    for fs in groups.values():
        sigs = [f['d'] | (f['s'] << nd) for f in fs]
        union = 0
        for sig in sigs: union |= sig
        scope = tuple(i for i in range(union.bit_length()) if union >> i & 1 and i not in kmap)
        rmap = {q: j for j, q in enumerate(scope)}
        terms = []
        for f, sig in zip(fs, sigs):
            km = sum(((sig >> q) & 1) << j for q, j in kmap.items())
            rm = sum(((sig >> q) & 1) << j for q, j in rmap.items())
            terms.append((km, rm, f['e'], f['p']))
        compiled.append((scope, 1 - m.chans[fs[0]['chan']]['p'], terms))
    return compiled

def factors_for(compiled, states, emask):
    outer_cache = {0: np.ones(len(states))}
    factors = []
    for scope, p0, terms in compiled:
        full = any(km for km, _, _, _ in terms)
        size = len(states) if full else 1
        ix = np.arange(1 << len(scope), dtype=np.uint32)
        vals = np.full((size, len(ix)), p0)
        for km, rm, e, p in terms:
            if km not in outer_cache:
                outer_cache[km] = 1 - 2 * (np.bitwise_count(states & km) & 1).astype(np.int8)
            outer = outer_cache[km] if full else np.ones(1)
            inner = 1 - 2 * (np.bitwise_count(ix & rm) & 1).astype(np.int8)
            vals += (p * (-1 if (e & emask).bit_count() & 1 else 1)) * outer[:, None] * inner[None, :]
        vals = vals.reshape((size,) + (2,) * len(scope), order='F')
        factors.append((scope, vals))
    return factors

def contract_selector(factors, order, batch_size):
    peak_elements = 0
    for v in order:
        bucket = [f for f in factors if v in f[0]]
        factors = [f for f in factors if v not in f[0]]
        if not bucket: continue
        union = tuple(sorted(set().union(*(set(s) for s, _ in bucket))))
        n = max(a.shape[0] for _, a in bucket)
        out = np.ones((n,) + (2,) * len(union))
        peak_elements = max(peak_elements, out.size)
        for scope, a in bucket:
            out *= a.reshape((a.shape[0],) + tuple(2 if u in scope else 1 for u in union))
        out = out.mean(axis=1 + union.index(v))
        factors.append((tuple(q for q in union if q != v), out))
    result = np.ones(batch_size)
    for scope, a in factors:
        assert not scope
        result *= a.reshape(-1)
    return result, peak_elements

def run(stem, nkeys=72, canonicalize=False):
    start = time.perf_counter()
    m, eng, groups, nd, ks, psi, where, dense_elim = prepare(stem,canonicalize)
    compiled = compile_channels(m, groups, nd, ks)
    elim = minfill([set(scope) for scope, _, _ in compiled])
    keys = [None] + eng.keys[:nkeys]
    rows = []
    for key in keys:
        t = time.perf_counter()
        states,weights,omission_bound=sparse_kernel(eng,ks,psi,where,key)
        emask = 0 if key is None else emask_for(key)
        factors = factors_for(compiled, states, emask)
        vec, peak = contract_selector(factors, elim['order'], len(states))
        value = float(np.dot(weights, vec) / (1 << len(ks)))
        row = dict(key=key, value=value, kernel_nonzero=len(states), peak_bucket_elements=peak,
                   absolute_kernel_omission_bound=omission_bound,
                   seconds=time.perf_counter()-t)
        rows.append(row)
        print(json.dumps(row), flush=True)
    out = dict(source=str(stem), method='sparse kernel cutset conditioning',
               channels=len(m.chans), dense_width=dense_elim['width'], conditioned_width=elim['width'],
               conditioned_work_entries=elim['work_entries'], kernel_bits=len(ks), results=rows,
               canonical_detector_rows=canonicalize, detector_row_changes=m.detector_row_changes,
               seconds=time.perf_counter()-start)
    if nkeys >= len(eng.keys):
        A = rows[0]['value']
        obs = sum(w*b*r['value'] for w,b,r in zip(eng.W,eng.beta,rows[1:]))
        out.update(acceptance=A, loss=(A-obs)/(2*A))
        eA=rows[0]['absolute_kernel_omission_bound']
        eO=sum(abs(w*b)*r['absolute_kernel_omission_bound'] for w,b,r in zip(eng.W,eng.beta,rows[1:]))
        out['conditional_loss_kernel_omission_bound']=eO/(2*(A-eA))+abs(obs)*eA/(2*A*(A-eA))
        out['omission_bound_note']='Bounds sparse cutoff error for computed kernel coefficients; excludes floating point roundoff.'
    print(json.dumps({k:v for k,v in out.items() if k!='results'}), flush=True)
    Path(__file__).with_name(stem.name+('_canonical' if canonicalize else '')+'_sparse_result.json').write_text(json.dumps(out,indent=2)+'\n')
    return out

if __name__ == '__main__':
    stem = Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'examples/v29c'
    nkeys = int(sys.argv[2]) if len(sys.argv)>2 else 72
    run(stem,nkeys,len(sys.argv)>3 and sys.argv[3]=='canonical')
