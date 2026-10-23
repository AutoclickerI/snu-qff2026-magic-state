"""Generalized final superdense cycle: per-tile op layers including where the Bell-pair readout
CX ("unbell") goes, and which ancilla of the pair is read in X. Ops of the X-read ancilla after
the unbell may only be X-part (ancilla -> data), of the Z-read one only Z-part (data -> ancilla).
Annealed against proxy2 (second-order loss of the cycle; Stim also rejects invalid cycles there).
"""
import json
import random
import sys

import cultiv_port as cp
import proxy2

TILES = proxy2.TILES
P = cp.phys


def ancilla_of(m, d):
    mx, my = m
    return (mx, my) if d in ((mx - 1, my), (mx, my + 1), (mx, my - 1)) else (mx + 1, my)


KEYS = [(t, d, typ) for t, (m, ds) in enumerate(TILES) for d in ds for typ in "XZ"] + [(t, "U", "") for t in range(3)]


def qubits_of(key, orient):
    t, d, typ = key
    m = TILES[t][0]
    if d == "U":
        return (m, (m[0] + 1, m[1]))
    return (ancilla_of(m, d), d)


def readers(t, orient):
    m = TILES[t][0]
    n = (m[0] + 1, m[1])
    return (m, n) if orient[t] == 0 else (n, m)    # (X-read, Z-read)


def feasible(assign, orient):
    used = set()
    for k, L in assign.items():
        for q in qubits_of(k, orient):
            if (L, q) in used:
                return False
            used.add((L, q))
    for t in range(3):
        u = assign[(t, "U", "")]
        ax, az = readers(t, orient)
        for (tt, d, typ), L in assign.items():
            if tt != t or d == "U" or L < u:
                continue
            q = ancilla_of(TILES[t][0], d)
            if (q == ax and typ != "X") or (q == az and typ != "Z"):
                return False
    return True


def emit(c, assign, orient):
    lmax = max(assign.values())
    xm = [P(m) for m, _ in TILES]
    zm = [P((m[0] + 1, m[1])) for m, _ in TILES]
    involved = sorted(set(xm) | set(zm) | set(cp.DATA))
    c.barrier(*involved)
    c.rx(*xm); c.reset(*zm)
    c.barrier(*involved)
    for a, b in zip(xm, zm):
        c.cx(a, b)
    last = {t: max(L for k, L in assign.items() if k[0] == t) for t in range(3)}
    for L in range(2, lmax + 2):
        c.barrier(*involved)
        for t in range(3):
            if last[t] == L - 1:
                ax, az = readers(t, orient)
                c.detector(c.mx(P(ax)))
                c.detector(c.measure(P(az)))
        for (t, d, typ), LL in sorted(assign.items(), key=lambda kv: str(kv[0])):
            if LL != L:
                continue
            if d == "U":
                ax, az = readers(t, orient)
                c.cx(P(ax), P(az))
            elif typ == "X":
                c.cx(P(ancilla_of(TILES[t][0], d)), P(d))
            else:
                c.cx(P(d), P(ancilla_of(TILES[t][0], d)))


UMAX = None   # if set: penalize unbells after this layer (forces post-unbell data ops)


def cost(assign, orient):
    if not feasible(assign, orient):
        return None
    try:
        v = proxy2.proxy(lambda c: emit(c, assign, orient), q_in=0)["cost"]
    except ValueError:
        return None
    if UMAX is not None:
        v += 2e-5 * sum(max(0, assign[(t, "U", "")] - UMAX) for t in range(3))
    return v


def v4_start():
    import cycle_opt as co
    best = json.load(open("batch_1792737466.json"))
    spec = [r for r in best if r["passed"]][0]["spec"]
    lay = co.plan(tuple(map(tuple, spec["pf"])), tuple(map(tuple, spec["ps"])), spec["first"])
    assign = {}
    for L, ops in lay.items():
        for part, anc, d in ops:
            t = next(t for t, (m, ds) in enumerate(TILES) if d in ds and ancilla_of(m, d) == anc)
            assign[(t, d, part)] = L
    for t in range(3):
        assign[(t, "U", "")] = 8
    return assign, [0, 0, 0]


def anneal(seed, steps, lmax, T0=4e-6, T1=2e-7, start=None):
    rng = random.Random(seed)
    assign, orient = start if start else v4_start()
    assign = dict(assign)
    cur = cost(assign, orient)
    best = (cur, dict(assign), list(orient))
    for s in range(steps):
        T = T0 * (T1 / T0) ** (s / steps)
        a2, o2 = dict(assign), list(orient)
        r = rng.random()
        if r < 0.1:
            o2[rng.randrange(3)] ^= 1
        elif r < 0.4:
            k = rng.choice(KEYS)
            a2[k] = rng.randint(2, lmax)
        elif r < 0.6:
            k1, k2 = rng.sample(KEYS, 2)
            a2[k1], a2[k2] = a2[k2], a2[k1]
        else:
            # move one op (often an unbell) to a layer; ops it collides with take its old layer
            k = rng.choice(KEYS) if r < 0.8 else (rng.randrange(3), "U", "")
            old, L = a2[k], rng.randint(2, lmax)
            qs = set(qubits_of(k, o2))
            for k2, L2 in list(a2.items()):
                if k2 != k and L2 == L and qs & set(qubits_of(k2, o2)):
                    a2[k2] = old
            a2[k] = L
        c2 = cost(a2, o2)
        if c2 is None:
            continue
        if c2 < cur or rng.random() < pow(2.718281828, -(c2 - cur) / T):
            assign, orient, cur = a2, o2, c2
            if cur < best[0]:
                best = (cur, dict(assign), list(orient))
    return best


def load(f, idx=0):
    import ast
    _, a, o, _ = json.load(open(f))[idx]
    return {(int(k[0]), ast.literal_eval(k[1]) if k[1] != "U" else "U", k[2]): L for k, L in a}, list(o)


def _job(args):
    seed, steps, lmax, start = args
    c, a, o = anneal(seed, steps, lmax, start=load(*start) if start else None)
    return c, [[list(map(str, k)), v] for k, v in a.items()], o, seed


if __name__ == "__main__":
    import multiprocessing as mp
    import time
    steps = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    lmax = int(sys.argv[2]) if len(sys.argv) > 2 else 9
    nchains = int(sys.argv[3]) if len(sys.argv) > 3 else 24
    start = (sys.argv[4], 0) if len(sys.argv) > 4 and sys.argv[4] != "-" else None
    if len(sys.argv) > 5:
        UMAX = int(sys.argv[5])
    a0, o0 = v4_start()
    print("v4 start cost", cost(a0, o0), flush=True)
    with mp.get_context("fork").Pool(nchains) as pool:
        res = pool.map(_job, [(100 + s, steps, lmax, start) for s in range(nchains)])
    res.sort(key=lambda r: r[0])
    for r in res[:10]:
        print(r[0], r[2], r[3])
    json.dump(res, open(f"gen_{lmax}_{int(time.time())}.json", "w"))
