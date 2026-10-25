"""All-orders pricing through MAIN/sparse with a per-circuit detector basis (INTEG2).

sparse_walsh.compile_best only applies reviewer 9's saved v36c basis; v36f falls back to the plain basis (width 12,
≈ 130 s at 16 processes). Here the same kind of basis (elementary XORs among zero-reference identity detector rows
outside the kernel scope: the accepted event and every moment are unchanged) is searched per circuit by reviewer 9's
hill-climb on (work_entries, width), then contracted. Exactness: the transform is invertible on accepted-event rows.

usage: ev2.py PROCS stem...   (stems are paths; results cached in res/<name>.json keyed by qasm sha256)
One stem: keys in parallel over PROCS. Several stems: stems in parallel, one process each.
"""
import os, sys, re, json, hashlib, time, io, contextlib, random
from pathlib import Path
for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[k] = '1'
sys.dont_write_bytecode = True
H = Path(__file__).resolve().parent
SP = H.parent / 'MAIN' / 'sparse'
sys.path.insert(0, str(SP))
import sparse_walsh as sw
RES = H / 'res'
RES.mkdir(exist_ok=True)
TRIALS = int(os.environ.get('BASIS_TRIALS', '1000'))
WARM = json.loads((H / os.environ.get('BASIS_WARM', 'warm_v36f.json')).read_text()) if os.environ.get('BASIS_WARM', 'warm_v36f.json') else None
_DETKEYS = None


def detkeys(text):
    return [','.join(map(str, sorted(map(int, re.findall(r'c\[(\d+)\]', l))))) for l in text.splitlines()
            if l.startswith('// DETECTOR')]


def find_ops(m, eng, groups, nd, ks, trials=TRIALS, seed=80353):
    """reviewer 9's hill-climb (random elementary XOR among free rows, keep if (work, width) drops), bitset min-fill."""
    from fastfill import minfill_adj
    faults = [f for fs in groups.values() for f in fs]
    chans = list(groups.keys())
    cidx = {c: j for j, c in enumerate(chans)}
    free = [i for i in range(nd) if i not in ks and tuple(eng.projs[i]) == (0, 0, 1) and int(eng.v[i]) == 0]
    rows = {i: sum(((f['d'] >> i) & 1) << j for j, f in enumerate(faults)) for i in range(nd) if i not in ks}
    cm = [0] * len(chans)
    for j, f in enumerate(faults):
        cm[cidx[f['chan']]] |= 1 << j
    inc = {i: {c for c in range(len(chans)) if rows[i] & cm[c]} for i in rows}
    scopes = [{i for i in rows if c in inc[i]} for c in range(len(chans))]
    cnt = {}
    mem = {}
    adj = {}

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

    for c, s in enumerate(scopes):
        tmp = set()
        for i in s:
            scopes[c] = tmp
            link(i, c, 1)
            tmp.add(i)
        scopes[c] = s
    base = minfill_adj(adj)
    rng = random.Random(seed)
    steps = []

    def xor(i, j):
        nr = rows[i] ^ rows[j]
        ni = {c for c in range(len(chans)) if nr & cm[c]}
        add, rem = ni - inc[i], inc[i] - ni
        for c in add:
            link(i, c, 1); scopes[c].add(i)
        for c in rem:
            scopes[c].discard(i); link(i, c, -1)
        return nr, ni, add, rem

    warm = WARM.get('ops') if WARM and _DETKEYS else None
    if warm:
        idx = {k: i for i, k in enumerate(_DETKEYS)}
        fs = set(free)
        for kt, ks_ in warm:
            i, j = idx.get(kt), idx.get(ks_)
            if i is None or j is None or i not in fs or j not in fs or i == j:
                continue
            nr, ni, _, _ = xor(i, j)
            rows[i] = nr; inc[i] = ni; steps.append([i, j])
    best = minfill_adj(adj)
    if len(free) < 2:
        return steps, base, best
    for _ in range(trials):
        i, j = rng.sample(free, 2)
        nr = rows[i] ^ rows[j]
        ni = {c for c in range(len(chans)) if nr & cm[c]}
        add, rem = ni - inc[i], inc[i] - ni
        if not add and not rem:
            continue
        for c in add:
            link(i, c, 1); scopes[c].add(i)
        for c in rem:
            scopes[c].discard(i); link(i, c, -1)
        ev = minfill_adj(adj)
        if ev < best:
            rows[i] = nr; inc[i] = ni; steps.append([i, j]); best = ev
        else:
            for c in add:
                scopes[c].discard(i); link(i, c, -1)
            for c in rem:
                link(i, c, 1); scopes[c].add(i)
    return steps, base, best


def compile_search(m, eng, groups, nd, kernel_scope):
    compiled = sw.compile_channels(m, groups, nd, kernel_scope)
    elim = sw.minfill([set(scope) for scope, _, _ in compiled])
    ops, _, _ = find_ops(m, eng, groups, nd, set(kernel_scope))
    if not ops:
        return compiled, elim
    rows = [1 << i for i in range(nd)]
    for target, source in ops:
        rows[target] ^= rows[source]
    moved = {c: [dict(f, d=sum(((f['d'] & r).bit_count() & 1) << i for i, r in enumerate(rows))) for f in fs]
             for c, fs in groups.items()}
    alt = sw.compile_channels(m, moved, nd, kernel_scope)
    alt_elim = sw.minfill([set(scope) for scope, _, _ in alt])
    sw._BASIS_INFO = dict(before=(elim['work_entries'], elim['width']), after=(alt_elim['work_entries'], alt_elim['width']),
                          ops=len(ops), warm=bool(WARM))
    sw._BASIS_OPS = [[_DETKEYS[a], _DETKEYS[b]] for a, b in ops] if _DETKEYS else None
    if (alt_elim['work_entries'], alt_elim['width']) < (elim['work_entries'], elim['width']):
        return alt, alt_elim
    return compiled, elim


sw.compile_best = compile_search


def one(args):
    st, procs = args
    st = Path(st).resolve()
    name = st.name
    sha = hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest()
    acc = os.environ.get('ACC_ONLY') == '1'
    out = RES / (name + ('.acc' if acc else '') + '.json')
    if out.exists():
        r = json.loads(out.read_text())
        if r.get('sha') == sha:
            return r
    t = time.time()
    global _DETKEYS
    _DETKEYS = detkeys(st.with_suffix('.qasm').read_text())
    try:
        cwd = os.getcwd(); os.chdir(SP)
        with contextlib.redirect_stdout(io.StringIO()):
            o = sw.run(st, 0 if acc else 72, True, procs)
        os.chdir(cwd)
        if acc:
            r = dict(name=name, sha=sha, seconds=time.time() - t, acceptance=o['results'][0]['value'])
            out.write_text(json.dumps(r))
            return r
        r = dict(name=name, sha=sha, seconds=time.time() - t, loss=o['loss'], acceptance=o['acceptance'],
                 bound=o['conditional_loss_kernel_omission_bound'], width=o['conditioned_width'],
                 work=o['conditioned_work_entries'], basis=getattr(sw, '_BASIS_INFO', None))
    except Exception as e:
        r = dict(name=name, sha=sha, error=repr(e))
    finally:
        (SP / (name + '_canonical_sparse_result.json')).unlink(missing_ok=True)
    out.write_text(json.dumps(r))
    return r


def price(stems, procs):
    """Generator of result dicts (stems in parallel when several)."""
    if len(stems) == 1:
        yield one((stems[0], procs))
        return
    import multiprocessing as mp
    with mp.get_context('fork').Pool(min(procs, len(stems))) as pool:
        for r in pool.imap_unordered(one, [(s, 1) for s in stems]):
            yield r


if __name__ == '__main__':
    procs = int(sys.argv[1])
    for r in price(sys.argv[2:], procs):
        print(json.dumps(r), flush=True)
