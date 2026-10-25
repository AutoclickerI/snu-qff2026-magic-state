"""Exhaustive GF(2) check of the A-flag round: which decoders / D->A timings / readout bases are valid, and how
many data gap ticks each needs.

Model (CSS, exact for the ideal circuit): A cells in |+_L> (code order A = [1,14,8,9,2,16,15]), data in the
Steane code with its logical maximally entangled with a reference R. The round = D->A CX (data i -> A_i, at a
chosen tick 42..44) plus A-A CX layers (oriented matchings on A's grid edges) at ticks 42..45, then every A
cell measured in X or Z (tick 46). B->D is at 45 for every data qubit, so data i has 44 - t(D->A_i) gap ticks.
Valid = (a) the data logical survives without a frame (L_X, L_Z keep deterministic signs), (b) the
deterministic Z-record parities read all three data Z-stabilizers (full-rank X-syndrome), (c) a flag: a
deterministic X-record parity; flag strength = number of the 21 weight-2 Z pairs (and 7 weight-3 Z_L lines)
on A at the round start that the deterministic X-parities detect (v36h's decoder: 12 pairs, 7 lines).
Prep gates (A-A CX at 43 before a cell's coupling) are included; tick 44 gates need both cells free of D->A.

usage: flagenum.py [maxgap]    prints the gap placements and writes flagenum_g<maxgap>.json
"""
import sys, json, itertools
from functools import lru_cache

A = [1, 14, 8, 9, 2, 16, 15]
D = [0, 20, 7, 10, 3, 22, 21]
SUP = ({0, 2, 4, 6}, {1, 2, 5, 6}, {3, 4, 5, 6})
NA, ND = 7, 7
NQ = NA + ND + 1          # A 0..6, D 7..13, R 14
R = 14


def bit(i):
    return 1 << i


def vec(idx, off):
    v = 0
    for i in idx:
        v |= bit(off + i)
    return v


def adj(a, b):
    ra, ca = divmod(a, 6)
    rb, cb = divmod(b, 6)
    return abs(ra - rb) + abs(ca - cb) == 1


EDGES = [(i, j) for i in range(NA) for j in range(NA) if i != j and adj(A[i], A[j])]   # directed c->t

# initial CSS stabilizers
SX = [vec(s, 0) for s in SUP] + [vec(range(7), 0)] + [vec(s, NA) for s in SUP] + [vec(range(7), NA) | bit(R)]
SZ = [vec(s, 0) for s in SUP] + [vec(s, NA) for s in SUP] + [vec(range(7), NA) | bit(R)]
IX_LX = 7          # index of X_L(D)X_R in SX
DZ = [vec(s, NA) for s in SUP]
AMASK = (1 << NA) - 1
DMASK = ((1 << ND) - 1) << NA


def reduce_basis(vs):
    """Row-echelon basis as dict pivot->vector (pivot = highest bit)."""
    basis = {}
    for v in vs:
        v = reduce_vec(basis, v)
        if v:
            basis[v.bit_length() - 1] = v
    return basis


def reduce_vec(basis, v):
    while v:
        h = v.bit_length() - 1
        if h in basis:
            v ^= basis[h]
        else:
            return v
    return 0


BX = reduce_basis(SX)
BZ = reduce_basis(SZ)
BX_noLX = reduce_basis(SX[:IX_LX])


def in_span(basis, v):
    return reduce_vec(basis, v) == 0


def canon(basis, v):
    """Canonical residue of v modulo span(basis) (linear projection; basis keyed by distinct leading bits)."""
    for h in sorted(basis, reverse=True):
        if (v >> h) & 1:
            v ^= basis[h]
    return v


def matchings(free):
    """All oriented matchings (lists of (c,t)) on A edges among cells in `free`."""
    und = sorted({(min(c, t), max(c, t)) for c, t in EDGES if c in free and t in free})
    out = []

    def rec(k, used, cur):
        if k == len(und):
            out.append(list(cur))
            return
        rec(k + 1, used, cur)
        a, b = und[k]
        if a not in used and b not in used:
            for c, t in ((a, b), (b, a)):
                cur.append((c, t))
                rec(k + 1, used | {a, b}, cur)
                cur.pop()
    rec(0, frozenset(), [])
    return out


def pullbacks(gates):
    """gates: time-ordered list of (c,t) qubit indices in the 15-qubit model. Returns px[k], pz[k] for A cells."""
    px, pz = [], []
    for k in range(NA):
        x, z = bit(k), bit(k)
        for c, t in reversed(gates):
            if (x >> c) & 1:
                x ^= bit(t)
            if (z >> t) & 1:
                z ^= bit(c)
        px.append(x)
        pz.append(z)
    return px, pz


def forward(gates, x=0, z=0):
    for c, t in gates:
        if (x >> c) & 1:
            x ^= bit(t)
        if (z >> t) & 1:
            z ^= bit(c)
    return x, z


def span_det(vs, idx, basis):
    """Deterministic parities among records idx (pullbacks vs): basis of subsets (bitmask over idx positions)
    whose pullback sum lies in span(basis). Returns list of (mask, sum)."""
    # Gaussian elimination on [v reduced mod basis | identity]
    rows = []
    for j, k in enumerate(idx):
        rows.append([canon(basis, vs[k]), 1 << j, vs[k]])
    # eliminate the residual part
    piv = {}
    out = []
    for r in rows:
        res, m, s = r
        while res:
            h = res.bit_length() - 1
            if h in piv:
                pr = piv[h]
                res ^= pr[0]
                m ^= pr[1]
                s ^= pr[2]
            else:
                break
        if res:
            piv[res.bit_length() - 1] = [res, m, s]
        else:
            out.append((m, s))
    return out


PAIRS = [vec(p, 0) for p in itertools.combinations(range(7), 2)]


def lines():
    grp = []
    for c in range(1, 8):
        s = 0
        for i in range(3):
            if (c >> i) & 1:
                s ^= vec(SUP[i], 0)
        grp.append(s)
    return [AMASK ^ s for s in grp]


LINE_VECS = lines()


def parity(v):
    return bin(v).count("1") & 1


def evaluate(gates, basis_mask, pb=None):
    """basis_mask bit k = 1 -> A cell k measured in X. Returns None if invalid, else (pairs, lines) detected."""
    px, pz = pb if pb is not None else pullbacks(gates)
    xs = [k for k in range(NA) if (basis_mask >> k) & 1]
    zs = [k for k in range(NA) if not (basis_mask >> k) & 1]
    # (b) full-rank data X-syndrome from deterministic Z-record parities
    detz = span_det(pz, zs, BZ)
    dparts = reduce_basis([s & DMASK for _, s in detz])
    if not all(in_span(dparts, d) for d in DZ):
        return None
    # (a) logical X survives without frame: some L_X = X_L(D)X_R + s commuting with every Z-record pullback,
    # whose forward image's A part sits on X-measured cells with a deterministic record parity.
    gens = SX[:IX_LX]
    ok = False
    for m in range(1 << len(gens)):
        lx = SX[IX_LX]
        for i in range(len(gens)):
            if (m >> i) & 1:
                lx ^= gens[i]
        if any(parity(lx & pz[k]) for k in zs):
            continue
        fx, _ = forward(gates, x=lx)
        w = fx & AMASK
        if any((w >> k) & 1 for k in zs):
            continue
        tot = 0
        for k in xs:
            if (w >> k) & 1:
                tot ^= px[k]
        if in_span(BX, tot):
            ok = True
            break
    if not ok:
        return None
    # logical Z: Z_L(D)Z_R must commute with X-record pullbacks (it does when they have no data part)
    lz = SZ[-1]
    if any(parity(lz & px[k]) for k in xs):
        return None
    # (c) flag: deterministic X-record parities; their A parts at the round start
    detx = span_det(px, xs, BX)
    aparts = [s & AMASK for _, s in detx]
    if not any(aparts):
        return (0, 0)
    pairs = sum(1 for p in PAIRS if any(parity(p & a) for a in aparts))
    lns = sum(1 for l in LINE_VECS if any(parity(l & a) for a in aparts))
    return (pairs, lns)


def build(dta, layers):
    """dta: tick of D->A per index; layers: {tick: [(c,t),...]} on A indices. Time-ordered gate list."""
    gates = []
    for t in range(40, 47):
        for i in range(NA):
            if dta[i] == t:
                gates.append((NA + i, i))
        for c, tt in layers.get(t, []):
            gates.append((c, tt))
    return gates


def _job(arg):
    dta, l43 = arg
    busy = {t: {i for i in range(NA) if dta[i] == t} for t in (42, 43, 44, 45)}
    free = {t: set(range(NA)) - busy[t] for t in busy}
    out, n = [], 0
    for l44 in matchings(free[44]):
        for l45 in matchings(free[45]):
            gates = build(dta, {43: l43, 44: l44, 45: l45})
            pb = pullbacks(gates)
            for bm in range(1, 1 << NA):
                n += 1
                r = evaluate(gates, bm, pb)
                if r is not None and r[0] + r[1] > 0:
                    out.append(dict(gap=sum(44 - t for t in dta),
                                    gapdata=[D[i] for i in range(NA) for _ in range(44 - dta[i])],
                                    dta={D[i]: dta[i] for i in range(NA)},
                                    L43=[(A[c], A[t]) for c, t in l43],
                                    L44=[(A[c], A[t]) for c, t in l44],
                                    L45=[(A[c], A[t]) for c, t in l45],
                                    X=[A[k] for k in range(NA) if (bm >> k) & 1],
                                    pairs=r[0], lines=r[1]))
    return n, out


def run(maxgap, procs=16):
    import multiprocessing as mp
    jobs = []
    for dta in itertools.product((42, 43, 44), repeat=NA):
        if sum(44 - t for t in dta) <= maxgap:
            free43 = {i for i in range(NA) if dta[i] != 43}
            for l43 in matchings(free43):
                jobs.append((dta, l43))
    with mp.get_context('fork').Pool(procs) as pool:
        parts = pool.map(_job, jobs, chunksize=1)
    return sum(n for n, _ in parts), [r for _, o in parts for r in o]


if __name__ == "__main__":
    maxgap = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    # self-test: v36h's decoder (D->A 43 for q10,q21; CX9->15 @44, CX8->9 @45; MX8)
    i = {q: k for k, q in enumerate(A)}
    dta = tuple(43 if D[k] in (10, 21) else 44 for k in range(NA))
    gates = build(dta, {44: [(i[9], i[15])], 45: [(i[8], i[9])]})
    bm = 1 << i[8]
    print("v36h decoder:", evaluate(gates, bm))
    gates_nodec = build(tuple([44] * 7), {})
    print("no decoder (all Z):", evaluate(gates_nodec, 0))
    nconf, res = run(maxgap)
    print(f"configurations checked: {nconf}; valid with a flag: {len(res)}")
    by = {}
    for r in res:
        key = (r['gap'], tuple(sorted(r['gapdata'])))
        b = by.setdefault(key, [0, 0, None])
        b[0] += 1
        if b[2] is None or (r['pairs'], r['lines']) > (b[2]['pairs'], b[2]['lines']):
            b[2] = r
        b[1] = max(b[1], r['pairs'])
    for key in sorted(by):
        n, mp, best = by[key]
        print(f"gap {key[0]} on {list(key[1])}: {n} valid configs; best flag {best['pairs']} pairs/{best['lines']} lines:"
              f" L43 {best['L43']} L44 {best['L44']} L45 {best['L45']} X {best['X']}")
    json.dump(dict(maxgap=maxgap, nconf=nconf, results=res), open(f"flagenum_g{maxgap}.json", "w"))
