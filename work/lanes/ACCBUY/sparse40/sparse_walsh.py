"""Sparse Fourier-kernel cutset contraction of the reviewer Walsh model.

Nonzero kernel assignments become a selector axis. All remaining detector
variables are summed exactly; no Monte Carlo or fault-order truncation.
The upstream kernel's numerical zero threshold is separately reported.
"""
import json, math, random, sys, time
from collections import defaultdict
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parent
import frontend as fa
from frontend import parse_current
from fastfill import adj_of, minfill_adj
def minfill(scopes):
    """Min-fill elimination order (key (fill, degree, vertex)) by fastfill's bitset graph."""
    order = []
    work, width = minfill_adj(adj_of(scopes), order)
    return dict(width=width, work_entries=work, order=order)

HADAMARD = {}

def fwht(a):
    """Unnormalized Walsh-Hadamard transform over every index bit, as dense Hadamard blocks of up to 6 bits (BLAS)."""
    a = np.asarray(a, dtype=float).reshape(-1)
    n, lo = a.size.bit_length() - 1, 0
    while lo < n:
        k = min(6, n - lo)
        if k not in HADAMARD:
            h = np.ones((1, 1))
            for _ in range(k): h = np.block([[h, h], [h, -h]])
            HADAMARD[k] = h
        a = a.reshape(-1, 1 << k) @ HADAMARD[k] if lo == 0 else np.matmul(HADAMARD[k], a.reshape(-1, 1 << k, 1 << lo))
        lo += k
    return a.reshape(-1)

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
    # General nonzero logical frames/postselection need the full judge Model.
    if '// FRAME' in text or '// POSTSELECT' in text:
        raise ValueError('Prototype supports the current zero-frame/no-POSTSELECT family only')
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
    # Row s holds the state with rotation j's sign flipped where bit j of s is set; each rotation doubles the rows.
    psi = np.zeros((1,eng.N),dtype=np.complex128)
    psi[:,0] = 1
    for j,(mj,wj,coef,theta) in enumerate(eng.rot):
        turn = (1j*math.sin(theta)*coef)*(psi*eng.sgn(wj)[None,:])[:,eng.idx.astype(int)^mj]
        psi = np.concatenate([np.cos(theta)*psi + turn, np.cos(theta)*psi - turn])
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
    mj,wj,c = (0,0,1) if key is None else eng.Qs[key]
    group = np.zeros((eng.N,len(where)),dtype=np.complex128)
    for v,idx in enumerate(where): group[idx,v] = 1
    group *= (c*eng.sgn(wj))[:,None]
    perm = eng.idx.astype(int)^mj
    g = np.empty((len(psi),len(where)))
    for lo in range(0,len(psi),1024):   # row blocks keep the complex temporaries in cache (v36h: 26 -> 10 ms per key)
        block = psi[lo:lo+1024]
        mix = np.take(block,perm,axis=1)
        np.conjugate(mix,out=mix); mix *= block
        g[lo:lo+1024] = (mix @ group).real
    flat=fwht(g)
    small=np.abs(flat)<threshold
    # Each remaining normalized characteristic-factor contraction is bounded
    # by one in magnitude. This bounds omission error, not floating arithmetic.
    omission_bound=float(np.abs(flat[small]).sum()/(1<<len(ks)))
    states=np.flatnonzero(~small).astype(np.uint32)
    return states,flat[states],omission_bound

def compile_channels(m, groups, nd, kernel_scope):
    """Channels as character tables on their full signature images, merged by image (reviewer 11's coalescing).

    A channel takes identity with probability 1 - p and each fault alternative with its own probability. All full
    signatures (kernel, residual detector and observable bits) lie in the GF(2) span S of the alternatives'; with
    reduced generators g_1..g_r of S, a character y enters only through t_b = <y, g_b>, and the channel's factor is
    chi[t] = sum_c dist[c] (-1)^(t.c), the Walsh transform of its distribution over coordinates c in S. A uniform
    channel (every DEPOLARIZE1/2, X_ERROR, Z_ERROR) has two levels, p0+n*p at t=0 and p0-p elsewhere. Channels with
    equal S multiply their tables. Returns entries (scope, chi, gens, sources): gens = (kernel mask, scope mask,
    observable mask) per generator, sources = [(channel, its chi)] for per-channel attribution."""
    kmap = {q: j for j, q in enumerate(kernel_scope)}
    shift = nd + len(m.rots)
    merged = {}
    for c, fs in groups.items():
        vecs = [f['d'] | (f['s'] << nd) | (f['e'] << shift) for f in fs]
        piv = {}
        for v in vecs:
            while v:
                h = v.bit_length() - 1
                if h not in piv:
                    piv[h] = v
                    break
                v ^= piv[h]
        heads = sorted(piv)
        for i, h in enumerate(heads):
            for g in heads[i + 1:]:
                if piv[g] >> h & 1: piv[g] ^= piv[h]
        dist = np.zeros(1 << len(heads))
        dist[0] = 1 - m.chans[c]['p']
        for v, f in zip(vecs, fs):
            dist[sum((v >> h & 1) << b for b, h in enumerate(heads))] += f['p']
        chi = fwht(dist)
        entry = merged.setdefault(tuple(piv[h] for h in heads), [1., []])
        entry[0] = entry[0] * chi
        entry[1].append((c, chi))
    compiled = []
    for basis, (chi, sources) in merged.items():
        union = 0
        for v in basis: union |= v
        scope = tuple(i for i in range(min(union.bit_length(), shift)) if union >> i & 1 and i not in kmap)
        rmap = {q: j for j, q in enumerate(scope)}
        gens = tuple((sum(((v >> q) & 1) << j for q, j in kmap.items()), sum(((v >> q) & 1) << j for q, j in rmap.items()),
                      v >> shift) for v in basis)
        compiled.append((scope, chi, gens, sources))
    return compiled

WARM = ROOT/'basis_warm.json'   # saved detector-row XOR sequences keyed by detector record sets (v36c, v36f families)
BASIS_TRIALS = 1000
SEARCH_WIDTH = 9

def search_basis(m, eng, groups, nd, kernel_scope, warm, trials=BASIS_TRIALS, seed=80353):
    """Detector-row XORs among zero-reference identity rows outside the kernel scope (the accepted event and every moment
    are unchanged; only contraction coordinates move): replay a saved sequence where its rows exist, then reviewer 9's
    hill-climb (random elementary XOR, kept if min-fill (work, width) drops). Returns (ops, (work, width))."""
    faults = [f for fs in groups.values() for f in fs]
    chans = list(groups)
    cidx = {c: j for j, c in enumerate(chans)}
    free = [i for i in range(nd) if i not in kernel_scope and tuple(eng.projs[i]) == (0, 0, 1) and int(eng.v[i]) == 0]
    rows = {i: 0 for i in range(nd) if i not in kernel_scope}
    for j, f in enumerate(faults):
        d = f['d']
        while d:
            b = d & -d; d ^= b; i = b.bit_length() - 1
            if i in rows: rows[i] |= 1 << j
    cm = [0] * len(chans)
    for j, f in enumerate(faults):
        cm[cidx[f['chan']]] |= 1 << j
    inc = {i: {c for c in range(len(chans)) if rows[i] & cm[c]} for i in rows}
    scopes = [set() for _ in chans]
    cnt, mem, adj = {}, {}, {}

    def link(i, c, d):
        mem[i] = mem.get(i, 0) + d
        for w in scopes[c]:
            if w == i:
                continue
            k = (min(i, w), max(i, w))
            n0 = cnt.get(k, 0)
            cnt[k] = n0 + d
            if n0 == 0 and d > 0:
                adj[i] = adj.get(i, 0) | (1 << w); adj[w] = adj.get(w, 0) | (1 << i)
            elif n0 + d == 0:
                adj[i] &= ~(1 << w); adj[w] &= ~(1 << i)
        if mem[i] > 0:
            adj.setdefault(i, 0)
        elif i in adj:
            del adj[i]

    def move(i, ni):
        add, rem = ni - inc[i], inc[i] - ni
        for c in add:
            link(i, c, 1); scopes[c].add(i)
        for c in rem:
            scopes[c].discard(i); link(i, c, -1)
        return add, rem

    for i in rows:
        for c in inc[i]:
            link(i, c, 1); scopes[c].add(i)
    keys = {','.join(map(str, sorted(d))): i for i, d in enumerate(m.dets)}
    fs, ops = set(free), []
    for kt, ksrc in warm:
        i, j = keys.get(kt), keys.get(ksrc)
        if i is None or j is None or i == j or i not in fs or j not in fs:
            continue
        rows[i] ^= rows[j]
        ni = {c for c in range(len(chans)) if rows[i] & cm[c]}
        move(i, ni); inc[i] = ni; ops.append((i, j))
    best = minfill_adj(adj)
    rng = random.Random(seed)
    for _ in range(trials if len(free) > 1 else 0):
        i, j = rng.sample(free, 2)
        nr = rows[i] ^ rows[j]
        ni = {c for c in range(len(chans)) if nr & cm[c]}
        add, rem = move(i, ni)
        if not add and not rem:
            continue
        cost = minfill_adj(adj)
        if cost < best:
            rows[i], inc[i], best = nr, ni, cost; ops.append((i, j))
        else:
            for c in add:
                scopes[c].discard(i); link(i, c, -1)
            for c in rem:
                link(i, c, 1); scopes[c].add(i)
    return ops, best

def compile_best(m, eng, groups, nd, kernel_scope):
    """compile_channels and its min-fill plan in the cheapest detector basis found: the plain one, or a saved sequence
    from basis_warm.json replayed on this circuit; only when the best of those is still wide (> SEARCH_WIDTH, where each
    width step doubles the contraction) is it refined by BASIS_TRIALS hill-climb steps (v36h: 12 s of search saved 18% of
    the work estimate and none of the 6 s contraction; v36f with the plain basis: width 12, ~130 s)."""
    compiled = compile_channels(m, groups, nd, kernel_scope)
    elim = minfill([set(e[0]) for e in compiled])
    warms = list(json.loads(WARM.read_text())['bases'].values())
    ops, cost = min((search_basis(m, eng, groups, nd, set(kernel_scope), w, trials=0) for w in warms),
                    key=lambda r: r[1])
    if min(cost, (elim['work_entries'], elim['width']))[1] > SEARCH_WIDTH:
        ops = min((search_basis(m, eng, groups, nd, set(kernel_scope), w) for w in warms), key=lambda r: r[1])[0]
    if ops:
        rows = [1 << i for i in range(nd)]
        for target, source in ops:
            rows[target] ^= rows[source]
        cols = [sum(((r >> i) & 1) << t for t, r in enumerate(rows)) for i in range(nd)]   # new rows containing old i
        def move(d):
            out = 0
            while d:
                b = d & -d; d ^= b; out ^= cols[b.bit_length() - 1]
            return out
        moved = {c: [dict(f, d=move(f['d'])) for f in fs] for c, fs in groups.items()}
        alt = compile_channels(m, moved, nd, kernel_scope)
        alt_elim = minfill([set(e[0]) for e in alt])
        if (alt_elim['work_entries'], alt_elim['width']) < (elim['work_entries'], elim['width']):
            compiled, elim = alt, alt_elim
    return compiled, elim

def patterns(scope, gens, states, emask, parity):
    """The character (state, scope assignment, emask) against gens as a pattern index row[state] ^ col[assignment];
    parity caches kernel-mask parities over states."""
    ix = np.arange(1 << len(scope), dtype=np.uint32)
    row, col = np.zeros(1, dtype=np.intp), np.zeros(len(ix), dtype=np.intp)
    for b, (km, rm, e) in enumerate(gens):
        col ^= ((np.bitwise_count(ix & rm) & 1) ^ ((e & emask).bit_count() & 1)).astype(np.intp) << b
        if km:
            if km not in parity:
                parity[km] = (np.bitwise_count(states & km) & 1).astype(np.intp)
            row = row ^ (parity[km] << b)
    return row, col

COLUMNS = {}

def columns(scope, union):
    """For each assignment of union (bit k <-> union[k]), the column of a factor over scope (bit j <-> scope[j])."""
    if (scope, union) not in COLUMNS:
        u, col = np.arange(1 << len(union)), np.zeros(1 << len(union), dtype=np.intp)
        for j, q in enumerate(scope):
            col |= ((u >> union.index(q)) & 1) << j
        COLUMNS[scope, union] = col
    return COLUMNS[scope, union]

def multiply(out, a):
    """out * a (batch 1 broadcasts), reusing the larger fresh array."""
    if out is None: return a
    if out.shape[0] < a.shape[0]: out, a = a, out
    out *= a
    return out

def factors_for(compiled, states, emask, order=None):
    """Factors (scope, array (selector or 1, 2^|scope|), column bit j <-> scope[j]): with an elimination order, one per
    bucket that first consumes entries (their scope's first eliminated variable; scope-less entries last), else one per
    entry; each is the product of its entries' chi at the character's pattern. States enter only through the parities
    of the group's kernel masks, so the product is built on one representative state per distinct parity pattern and
    gathered back."""
    groups = defaultdict(list)
    pos = {v: i for i, v in enumerate(order or [])}
    for i, e in enumerate(compiled):
        groups[min((pos[v] for v in e[0]), default=len(pos)) if order else i].append(i)
    parity = {}
    factors = []
    for group in groups.values():
        entries = [compiled[i] for i in group]
        scope = tuple(sorted(set().union(*(e[0] for e in entries))))
        piv = {}
        for v in {km for e in entries for km, _, _ in e[2]}:
            while v:
                h = v.bit_length() - 1
                if h not in piv:
                    piv[h] = v
                    break
                v ^= piv[h]
        reps, inverse = states[:0], None
        if piv:
            rho = np.zeros(len(states), dtype=np.int64)
            for b, v in enumerate(piv.values()):
                if v not in parity:
                    parity[v] = (np.bitwise_count(states & v) & 1).astype(np.intp)
                rho |= parity[v] << b
            _, first, inverse = np.unique(rho, return_index=True, return_inverse=True)
            reps = states[first]
        out = None
        for escope, chi, gens, _ in sorted(entries, key=lambda e: any(km for km, _, _ in e[2])):
            row, col = patterns(escope, gens, reps, emask, {})
            out = multiply(out, chi[np.arange(len(chi))[:, None] ^ col[columns(escope, scope)][None, :]][row])
        factors.append((scope, out if inverse is None else out[inverse]))
    return factors

CHUNK = 256   # selector rows per pass: bucket tensors (CHUNK x 2^width doubles) stay in cache; v36h with 8 concurrent
              # workers: 37 ms per moment against 94-104 ms unchunked

def contract_selector(factors, order, batch_size):
    """Bucket elimination with the selector as a batch axis, in independent chunks of CHUNK selector rows: each bucket
    gathers its factors onto the union's columns, multiplies them in place (selector-free ones first) and sums out its
    variable. Returns the selector vector and the largest bucket product (elements, per chunk)."""
    if batch_size > CHUNK:
        parts = [contract_selector([(s, a[lo:lo + CHUNK] if len(a) > 1 else a) for s, a in factors], order,
                                   min(CHUNK, batch_size - lo)) for lo in range(0, batch_size, CHUNK)]
        return np.concatenate([v for v, _ in parts]), max(p for _, p in parts)
    peak_elements = 0
    for v in order:
        bucket = [f for f in factors if v in f[0]]
        factors = [f for f in factors if v not in f[0]]
        if not bucket: continue
        union = tuple(sorted(set().union(*(s for s, _ in bucket))))
        out = None
        for scope, a in sorted(bucket, key=lambda f: f[1].shape[0]):
            out = multiply(out, np.take(a, columns(scope, union), axis=1))
        peak_elements = max(peak_elements, out.size)
        pairs = out.reshape(len(out), -1, 2, 1 << union.index(v))
        out = (pairs[:, :, 0] + pairs[:, :, 1]).reshape(len(out), -1)
        out *= 0.5
        factors.append((tuple(q for q in union if q != v), out))
    result = np.ones(batch_size)
    for scope, a in factors:
        assert not scope
        result *= a.reshape(-1)
    return result, peak_elements

def contract_quotient(compiled, states, emask, order):
    """factors_for + contract_selector without gathering back: a factor depends on the selector only through the
    parities of its kernel masks, so every factor and every bucket message is kept on one row per class of states
    with equal parities on its mask span, and is lifted to a bucket's (finer) classes only inside that bucket (reviewer
    12). Returns the selector vector and the largest bucket product (elements, per chunk)."""
    classes = {}
    def span(vecs):
        piv = {}
        for v in vecs:
            for h, w in sorted(piv.items(), reverse=True):
                if v >> h & 1: v ^= w
            if v: piv[v.bit_length() - 1] = v
        for h in sorted(piv):
            for g in piv:
                if g != h and piv[g] >> h & 1: piv[g] ^= piv[h]
        return tuple(piv[h] for h in sorted(piv))
    def cls(b):
        if b not in classes:
            rho = np.zeros(len(states), dtype=np.int64)
            for j, mask in enumerate(b):
                rho |= (np.bitwise_count(states & mask) & 1).astype(np.int64) << j
            classes[b] = np.unique(rho, return_index=True, return_inverse=True)[1:]
        return classes[b]
    pos = {v: i for i, v in enumerate(order)}
    groups = defaultdict(list)
    for e in compiled:
        groups[min((pos[v] for v in e[0]), default=len(pos))].append(e)
    factors = []
    for entries in groups.values():
        scope = tuple(sorted(set().union(*(set(e[0]) for e in entries))))
        b = span([km for e in entries for km, _, _ in e[2]])
        reps = cls(b)[0]
        out = None
        for escope, chi, gens, _ in sorted(entries, key=lambda e: any(km for km, _, _ in e[2])):
            row, col = patterns(escope, gens, states[reps], emask, {})
            out = multiply(out, chi[np.arange(len(chi))[:, None] ^ col[columns(escope, scope)][None, :]][row])
        factors.append((scope, b, out))
    peak_elements = 0
    for v in order:
        bucket = [f for f in factors if v in f[0]]
        factors = [f for f in factors if v not in f[0]]
        if not bucket: continue
        union = tuple(sorted(set().union(*(set(s) for s, _, _ in bucket))))
        b = span([m for _, bb, _ in bucket for m in bb])
        reps = cls(b)[0]
        result = np.empty((len(reps), 1 << (len(union) - 1)))
        for lo in range(0, len(reps), CHUNK):
            here = reps[lo:lo + CHUNK]
            out = None
            for scope, bb, a in sorted(bucket, key=lambda f: f[2].shape[0]):
                out = multiply(out, np.take(a[cls(bb)[1][here]], columns(scope, union), axis=1))
            peak_elements = max(peak_elements, out.size)
            pairs = out.reshape(len(out), -1, 2, 1 << union.index(v))
            result[lo:lo + len(here)] = (pairs[:, :, 0] + pairs[:, :, 1]).reshape(len(out), -1) * 0.5
        factors.append((tuple(q for q in union if q != v), b, result))
    result = np.ones(len(states))
    for scope, b, a in factors:
        assert not scope
        result *= a.reshape(-1)[cls(b)[1]]
    return result, peak_elements

_CTX = {}

def _row(key):
    eng, ks, psi, where, compiled, elim = (_CTX[k] for k in ('eng', 'ks', 'psi', 'where', 'compiled', 'elim'))
    t = time.perf_counter()
    states,weights,omission_bound=sparse_kernel(eng,ks,psi,where,key)
    emask = 0 if key is None else emask_for(key)
    vec, peak = contract_quotient(compiled, states, emask, elim['order'])
    value = float(np.dot(weights, vec) / (1 << len(ks)))
    return dict(key=key, value=value, kernel_nonzero=len(states), peak_bucket_elements=peak,
                absolute_kernel_omission_bound=omission_bound, seconds=time.perf_counter()-t)

def run(stem, nkeys=72, canonicalize=False, procs=1):
    """Each acceptance/observable key is an independent contraction; procs > 1 forks workers that share the
    prepared model and return rows in key order, so the result equals the serial run."""
    start = time.perf_counter()
    m, eng, groups, nd, ks, psi, where, dense_elim = prepare(stem,canonicalize)
    compiled, elim = compile_best(m, eng, groups, nd, ks)
    keys = [None] + eng.keys[:nkeys]
    _CTX.update(eng=eng, ks=ks, psi=psi, where=where, compiled=compiled, elim=elim)
    if procs > 1:
        import multiprocessing as mp
        with mp.get_context('fork').Pool(procs) as pool:
            rows = list(pool.imap(_row, keys))
    else:
        rows = [_row(key) for key in keys]
    for row in rows:
        print(json.dumps(row), flush=True)
    out = dict(source=str(stem), method='sparse kernel cutset conditioning',
               channels=len(m.chans), factors=len(compiled), dense_width=dense_elim['width'], conditioned_width=elim['width'],
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
    procs = int(sys.argv[4]) if len(sys.argv)>4 else 1
    run(stem,nkeys,len(sys.argv)>3 and sys.argv[3]=='canonical',procs)
