"""Search interleaved orderings of the d=3 superdense cycle (Bell pair per tile) so every data
qubit's last X-type and last Z-type CNOT land as late as possible.

Validity is checked exactly with Stim (noiseless): the cycle must report every stabilizer and
leave the code state (both logical bases) unchanged.
"""
import itertools
import random
import sys

import stim

import cultiv_port as cp

TILES = [((1, 0), [(3, 0), (0, 0), (1, 1), (2, 1)]),
         ((1, 2), [(3, 2), (1, 1), (2, 3), (2, 1)]),
         ((3, 1), [(2, 1), (3, 2), (3, 0), (4, 0)])]
SUPPORT_XY = [set(d) for _, d in TILES]


def ancilla_of(m, d):
    mx, my = m
    if d in ((mx - 1, my), (mx, my + 1), (mx, my - 1)):
        return (mx, my)
    return (mx + 1, my)


# all (tile, data) incidences with their ancilla
INC = [(t, m, d, ancilla_of(m, d)) for t, (m, ds) in enumerate(TILES) for d in ds]
DATA_XY = sorted({d for _, _, d, _ in INC})
P = cp.phys


def ops_of(assign):
    """assign[(t, d, typ)] = layer (2..LMAX). Returns list per layer of (typ, anc, d)."""
    out = {}
    for (t, d, typ), L in assign.items():
        m = TILES[t][0]
        out.setdefault(L, []).append((typ, ancilla_of(m, d), d))
    return out


def stim_cycle(assign, lmax):
    """Noiseless validity circuit: MPP-prepare the code state's stabilizers + a logical,
    run the cycle, MPP again; detectors compare everything."""
    lay = ops_of(assign)
    circs = []
    for logical in ("X", "Z"):
        c = stim.Circuit()
        stabs = [(B, s) for B in "XZ" for s in SUPPORT_XY]
        def mpp(B, s):
            c.append("MPP", [x for q in sorted(s, key=P) for x in (stim.target_pauli(P(q), B), stim.target_combiner())][:-1])
        for B, s in stabs:
            mpp(B, s)
        mpp(logical, DATA_XY)
        xm = [P(m) for m, _ in TILES]
        zm = [P((m[0] + 1, m[1])) for m, _ in TILES]
        c.append("RX", xm); c.append("R", zm)
        c.append("CX", [q for a, b in zip(xm, zm) for q in (a, b)])
        for L in range(2, lmax + 1):
            for typ, anc, d in lay.get(L, []):
                c.append("CX", [P(anc), P(d)] if typ == "X" else [P(d), P(anc)])
            c.append("TICK")
        c.append("CX", [q for a, b in zip(xm, zm) for q in (a, b)])
        c.append("MX", xm); c.append("M", zm)
        for B, s in stabs:
            mpp(B, s)
        mpp(logical, DATA_XY)
        # records: 7 initial, 3 MX, 3 M, 7 final  (total 20)
        n = 20
        rec = lambda i: stim.target_rec(i - n)
        for k in range(3):
            c.append("DETECTOR", [rec(7 + k), rec(k)])          # X anc vs X stab
            c.append("DETECTOR", [rec(10 + k), rec(3 + k)])     # Z anc vs Z stab
        for k in range(7):
            c.append("DETECTOR", [rec(13 + k), rec(k)])         # state preserved
        circs.append(c)
    return circs


def valid(assign, lmax):
    for c in stim_cycle(assign, lmax):
        s = c.compile_detector_sampler().sample(64)
        if s.any():
            return False
    return True


def feasible(assign):
    lay = ops_of(assign)
    for L, ops in lay.items():
        qs = [q for _, a, d in ops for q in (a, d)]
        if len(qs) != len(set(qs)):
            return False
    return True


def tail_cost(assign, lmax):
    lastX, lastZ = {}, {}
    for (t, d, typ), L in assign.items():
        tgt = lastX if typ == "X" else lastZ
        tgt[d] = max(tgt.get(d, 0), L)
    # Z-type output errors (undetected after last X-type CNOT) cost 1, X-type 1/2
    return sum(2 * (lmax - lastX[d]) + (lmax - lastZ[d]) for d in DATA_XY)


def random_assign(rng, lmax):
    keys = [(t, d, typ) for t, m, d, a in INC for typ in "XZ"]
    for _ in range(2000):
        assign, used = {}, set()
        ok = True
        rng.shuffle(keys)
        for k in keys:
            t, d, typ = k
            anc = ancilla_of(TILES[t][0], d)
            choices = [L for L in range(2, lmax + 1) if (L, d) not in used and (L, anc) not in used]
            if not choices:
                ok = False
                break
            # bias late
            L = max(choices) if rng.random() < 0.6 else rng.choice(choices)
            assign[k] = L
            used.add((L, d)); used.add((L, anc))
        if ok:
            return assign
    return None


def search(n=20000, lmax=7, seed=0):
    rng = random.Random(seed)
    best = {}
    for _ in range(n):
        a = random_assign(rng, lmax)
        if a is None or not feasible(a):
            continue
        cost = tail_cost(a, lmax)
        key = tuple(sorted(a.items()))
        if key in best:
            continue
        if len(best) > 400 and cost > max(v[0] for v in best.values()):
            continue
        if not valid(a, lmax):
            continue
        best[key] = (cost, a)
        if len(best) > 500:
            worst = max(best, key=lambda k: best[k][0])
            del best[worst]
    return sorted(best.values(), key=lambda x: x[0])


def emit(c, assign, lmax):
    lay = ops_of(assign)
    xm = [P(m) for m, _ in TILES]
    zm = [P((m[0] + 1, m[1])) for m, _ in TILES]
    involved = sorted(set(xm) | set(zm) | set(cp.DATA))
    c.barrier(*involved)
    c.rx(*xm); c.reset(*zm)
    c.barrier(*involved)
    for a, b in zip(xm, zm):
        c.cx(a, b)
    for L in range(2, lmax + 1):
        c.barrier(*involved)
        for typ, anc, d in lay.get(L, []):
            if typ == "X":
                c.cx(P(anc), P(d))
            else:
                c.cx(P(d), P(anc))
    c.barrier(*involved)
    for a, b in zip(xm, zm):
        c.cx(a, b)
    for q in xm:
        c.detector(c.mx(q))
    for q in zm:
        c.detector(c.measure(q))


def build_with(assign, lmax=7, lazy=True):
    from qcirc import Circ
    c = Circ()
    cp.run_chunk(c, cp.extract_chunk("make_chunk_d3_init_unitary", cp.UP + "_injection_stage.py"), s_to="Tswap")
    cp.run_chunk(c, cp.extract_chunk("make_chunk_d3_double_cat_check", cp.UP + "_cultivation_stage.py"), s_to="Tswap")
    emit(c, assign, lmax)
    return c.rescheduled(lazy_init=True) if lazy else c


if __name__ == "__main__":
    lmax = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    res = search(n=int(float(sys.argv[2])) if len(sys.argv) > 2 else 20000, lmax=lmax)
    print(len(res), "valid orderings kept; best tail costs", [r[0] for r in res[:15]])
    import pickle
    pickle.dump(res, open(f"interleave_l{lmax}.pkl", "wb"))
