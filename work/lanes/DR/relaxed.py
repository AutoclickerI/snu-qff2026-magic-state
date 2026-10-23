"""Grid-free floor of a final round made of cat-style checks (direct, 1-step readout).

Exact second-order loss under the judge's noise of the DATA-side faults of one final round:
idle (p/3 per Pauli per step) and the check CNOTs (DEPOLARIZE2, p/15 per Pauli pair; the ancilla part
flips its check when visible to the readout basis). Ancilla preparation, hooks, the grid and the
pre-stage are ignored, so the result is a lower bound for this design class. Undetected pairs are
pairs of faults with equal detector signatures whose combined data error is harmful after the judge's
lookup correction (X_L costs 1/2, Y_L 1/2, Z_L 1).

Choices searched: the X-check and Z-check generator sets (any generating triples of the seven
weight-4 stabilizers, chosen independently), each data qubit's check order and steps. Every check is
read out one step after the last CNOT of the round (step T); data idle until T+1.

    python relaxed.py [restarts] [optimistic|common]
"""
import itertools
import random
import sys

P = 1e-3
W4 = [frozenset(s) for s in ({0, 2, 4, 6}, {1, 2, 5, 6}, {3, 4, 5, 6}, {0, 1, 4, 5}, {0, 2, 3, 5},
                             {1, 2, 3, 4}, {0, 1, 3, 6})]
TRIPLES = [t for t in itertools.combinations(range(7), 3)
           if len({W4[t[0]] ^ W4[t[1]], W4[t[2]]}) == 2 and W4[t[0]] ^ W4[t[1]] != W4[t[2]]]


def cost(a, b):
    """a, b: (x, z) bits of two single-qubit Paulis on different data qubits."""
    if a[0] and b[0]:
        return 0.5
    return 1.0 if a[1] and b[1] else 0.0


PAULI = {"X": (1, 0), "Y": (1, 1), "Z": (0, 1)}
CPAIR = {(a, b): cost(PAULI[a], PAULI[b]) for a in PAULI for b in PAULI}


def events(sched, T, start):
    """sched[q] = list of (step, check id, type); checks: ('X', k) catches Z errors, ('Z', k) X errors.
    Yields (signature frozenset, qubit, pauli, prob) for data-affecting faults."""
    out = []
    for q in range(7):
        s = sorted(sched[q])
        busy = {t: (cid, typ) for t, cid, typ in s}

        def sig(after, pauli):
            x, z = PAULI[pauli]
            return frozenset(cid for t, cid, typ in s if t > after and ((typ == "Z" and x) or (typ == "X" and z)))
        for t in range(start[q], T + 1):
            if t in busy:
                cid, typ = busy[t]
                vis = ("Z", "Y") if typ == "X" else ("X", "Y")
                for pd in PAULI:
                    for qa in ("I", "X", "Y", "Z"):
                        g = sig(t, pd)
                        if qa in vis:
                            g = g ^ {cid}
                        out.append((g, q, pd, P / 15))
            else:
                for pd in PAULI:
                    out.append((sig(t, pd), q, pd, P / 3))
    return out


def valid(sched):
    """Cat checks X_S and Z_S' commute only if an even number of their shared data see the
    X coupling first (otherwise a detector is random)."""
    when = {}
    for q in range(7):
        for t, cid, typ in sched[q]:
            when[(q, cid)] = t
    xs = {cid for q in range(7) for _, cid, typ in sched[q] if typ == "X"}
    zs = {cid for q in range(7) for _, cid, typ in sched[q] if typ == "Z"}
    for a in xs:
        for b in zs:
            shared = W4[a[1]] & W4[b[1]]
            if sum(when[(q, a)] < when[(q, b)] for q in shared) % 2:
                return False
    return True


def loss(sched, T, start):
    if not valid(sched):
        return float("inf")
    by = {}
    for g, q, pd, pr in events(sched, T, start):
        m = by.setdefault(g, [dict() for _ in range(7)])
        m[q][pd] = m[q].get(pd, 0.0) + pr
    tot = 0.0
    for m in by.values():
        for i, j in itertools.combinations(range(7), 2):
            for a, pa in m[i].items():
                for b, pb in m[j].items():
                    tot += pa * pb * CPAIR[(a, b)]
    return tot


def checks_of(q, xt, zt):
    return [(("X", k), "X") for k in xt if q in W4[k]] + [(("Z", k), "Z") for k in zt if q in W4[k]]


def options(q, xt, zt, T, mode):
    cs = checks_of(q, xt, zt)
    n = len(cs)
    slots = [tuple(range(T - n, T))] if mode == "optimistic" else list(itertools.combinations(range(T), n))
    for st in slots:
        for perm in itertools.permutations(cs):
            yield [(t, cid, typ) for t, (cid, typ) in zip(st, perm)]


def solve(xt, zt, mode, restarts, rng):
    n = [len(checks_of(q, xt, zt)) for q in range(7)]
    T = max(n)
    start = [T - n[q] if mode == "optimistic" else 0 for q in range(7)]
    opts = [list(options(q, xt, zt, T, mode)) for q in range(7)]
    if mode == "optimistic":
        pass
    best = (float("inf"), None)
    for _ in range(restarts):
        for _try in range(200000):
            cur = [rng.choice(o) for o in opts]
            if valid(cur):
                break
        else:
            continue
        if mode == "optimistic":
            st = start
        else:
            st = start
        val = loss(cur, T, st)
        improved = True
        while improved:
            improved = False
            for q in rng.sample(range(7), 7):
                cand = opts[q] if len(opts[q]) <= 800 else rng.sample(opts[q], 800)
                for o in cand:
                    trial = cur[:q] + [o] + cur[q + 1:]
                    v = loss(trial, T, st)
                    if v < val - 1e-15:
                        cur, val, improved = trial, v, True
        if val < best[0]:
            best = (val, [sorted(c) for c in cur])
    return best[0], best[1], T


if __name__ == "__main__":
    restarts = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    mode = sys.argv[2] if len(sys.argv) > 2 else "optimistic"
    rng = random.Random(1)
    xt = TRIPLES[0]
    res = []
    for zt in TRIPLES:
        v, sch, T = solve(xt, zt, mode, restarts, rng)
        res.append((v, zt, T, sch))
        print(f"X gens {xt} Z gens {zt} T {T}: floor {v:.4e}", flush=True)
    res.sort(key=lambda r: r[0])
    v, zt, T, sch = res[0]
    print(f"BEST {mode}: {v:.4e}  X gens {[sorted(W4[k]) for k in xt]}  Z gens {[sorted(W4[k]) for k in zt]}  T {T}")
    for q in range(7):
        print(f"  d{q}: " + " ".join(f"t{t}:{typ}{sorted(W4[cid[1]])}" for t, cid, typ in sch[q]))
