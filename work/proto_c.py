"""Prototype C (no grid): compact injection, cat-based W check, and a final round of six flagged
checks with load-balanced generators packed into the last data slots (layered via barriers).

X checks: S1, S12, S123.  Z checks: S2, S13, S23.  Max data load 4.
"""
import itertools
import random
import sys

from qcirc import Circ, allow_any_coupling, evaluate

allow_any_coupling()
DATA = list(range(7))
W = {"S1": (0, 2, 4, 6), "S2": (1, 2, 5, 6), "S3": (3, 4, 5, 6), "S12": (0, 1, 4, 5),
     "S13": (0, 2, 3, 5), "S23": (1, 2, 3, 4), "S123": (0, 1, 3, 6)}
XCHK = ["S1", "S12", "S123"]
ZCHK = ["S2", "S13", "S23"]
CHECKS = [("X", w) for w in XCHK] + [("Z", w) for w in ZCHK]


def layered(c, layers, qubits):
    """Emit layers of ops; a barrier over `qubits` between layers fixes the time steps."""
    for k, layer in enumerate(layers):
        for op in layer:
            op(c)
        if k + 1 < len(layers):
            c.barrier(*qubits)


def plan_round(rng):
    """Random slot plan: each check gets start slot t in {0,1,2}; its 4 data split into two
    pairs (a-pair, f-pair), each ancilla doing one data at t and one at t+1. Returns per check
    (t, [(slot, data, who)]) or None if some data qubit is double-booked or the X/Z order on
    shared qubits is inconsistent."""
    plan = {}
    busy = {}
    for typ, w in CHECKS:
        t = rng.choice([0, 1, 2])
        d = list(W[w]); rng.shuffle(d)
        # a: d[0]@t, d[1]@t+1 ; f: d[2]@t, d[3]@t+1
        acts = [(t, d[0], "a"), (t + 1, d[1], "a"), (t, d[2], "f"), (t + 1, d[3], "f")]
        for s, q, _ in acts:
            if (s, q) in busy:
                return None
            busy[(s, q)] = (typ, w)
        plan[(typ, w)] = (t, acts)
    # commutation: for X check P and Z check Q sharing qubits, same order on all shared qubits
    for (tx, wx) in [(c) for c in CHECKS if c[0] == "X"]:
        for (tz, wz) in [(c) for c in CHECKS if c[0] == "Z"]:
            shared = set(W[wx]) & set(W[wz])
            order = set()
            for q in shared:
                sx = next(s for s, qq, _ in plan[("X", wx)][1] if qq == q)
                sz = next(s for s, qq, _ in plan[("Z", wz)][1] if qq == q)
                order.add(sx < sz)
            if len(order) > 1:
                return None
    return plan


def tail_cost(plan, end=3):
    lastX = {q: -1 for q in DATA}
    lastZ = {q: -1 for q in DATA}
    for (typ, w), (t, acts) in plan.items():
        for s, q, _ in acts:
            if typ == "X":
                lastX[q] = max(lastX[q], s)
            else:
                lastZ[q] = max(lastZ[q], s)
    # Z-type late errors (undetected after last X check) cost twice X-type ones
    return sum(2 * (end - lastX[q]) + (end - lastZ[q]) for q in DATA)


def all_plans(n_slots=4):
    """Exhaustive backtracking over slot plans (pairs of data at t and t+1; a/f split fixed:
    first of each pair to a). Yields (tail_cost, plan)."""
    from itertools import combinations
    opts = []
    for typ, w in CHECKS:
        o = []
        for t in range(n_slots - 1):
            for first in combinations(W[w], 2):
                second = [q for q in W[w] if q not in first]
                acts = [(t, first[0], "a"), (t + 1, second[0], "a"), (t, first[1], "f"), (t + 1, second[1], "f")]
                o.append((t, acts))
        opts.append(o)
    busy = {}
    chosen = [None] * len(CHECKS)

    def consistent(k):
        typ, w = CHECKS[k]
        for j in range(k):
            tj, wj = CHECKS[j]
            if tj == typ:
                continue
            shared = set(W[w]) & set(W[wj])
            order = set()
            for q in shared:
                s1 = next(s for s, qq, _ in chosen[k][1] if qq == q)
                s2 = next(s for s, qq, _ in chosen[j][1] if qq == q)
                order.add((s1 < s2) == (typ == "X"))
            if len(order) > 1:
                return False
        return True

    def rec(k):
        if k == len(CHECKS):
            plan = {CHECKS[i]: chosen[i] for i in range(len(CHECKS))}
            yield tail_cost(plan, n_slots - 1), plan
            return
        for opt in opts[k]:
            if any((s, q) in busy for s, q, _ in opt[1]):
                continue
            chosen[k] = opt
            if not consistent(k):
                continue
            for s, q, _ in opt[1]:
                busy[(s, q)] = k
            yield from rec(k + 1)
            for s, q, _ in opt[1]:
                del busy[(s, q)]
        chosen[k] = None

    yield from rec(0)


def best_plans(n_slots=4, keep=5):
    res = sorted(all_plans(n_slots), key=lambda x: x[0])
    return res[:keep]


def build(plan, w_order=None):
    c = Circ()
    # ancillas: W cat 7..9, checks: 10.. (a, f per check)
    anc = {}
    nxt = 10
    for chk in CHECKS:
        anc[chk] = (nxt, nxt + 1)
        nxt += 2
    allq = list(range(nxt))

    # --- injection (11 CX) ---
    c.rx(0, 1, 3, 2)
    c.t(2)
    c.cxs([(2, 4), (2, 5), (0, 2), (0, 4), (0, 6), (1, 2), (1, 5), (1, 6), (3, 4), (3, 5), (3, 6)])
    # --- W check: cat of 3 ancillas (7: d0,d1,d2  8: d3,d4  9: d5,d6) ---
    c.barrier(*allq)
    c.rx(7); c.reset(8, 9)
    c.cx(7, 8); c.cx(7, 9)
    c.t(*DATA)
    for a, ds in [(7, (0, 1, 2)), (8, (3, 4)), (9, (5, 6))]:
        for d in ds:
            c.cx(a, d)
    c.tdg(*DATA)
    bits = [c.mx(7), c.mx(8), c.mx(9)]
    c.detector(*bits)

    # --- final round, layered ---
    c.barrier(*allq)
    layers = [[] for _ in range(7)]   # 0: prep, 1: link, 2..5: data slots, ... flexible
    # For each check: prep at slot t (layer t), link at t+1, data at t+2,t+3, unlink t+4, measure t+5
    for (typ, w), (t, acts) in plan.items():
        a, f = anc[(typ, w)]
        L = t
        if typ == "X":
            layers[L].append(lambda c, a=a, f=f: (c.rx(a), c.reset(f)))
            layers[L + 1].append(lambda c, a=a, f=f: c.cx(a, f))
            for s, q, who in acts:
                g = a if who == "a" else f
                layers[s + 2].append(lambda c, g=g, q=q: c.cx(g, q))
            layers.extend([[] for _ in range(max(0, t + 6 - len(layers)))])
            layers[t + 4].append(lambda c, a=a, f=f: c.cx(a, f))
            layers[t + 5].append(lambda c, a=a, f=f: (c.detector(c.mx(a)), c.detector(c.measure(f))))
        else:
            layers[L].append(lambda c, a=a, f=f: (c.reset(a), c.rx(f)))
            layers[L + 1].append(lambda c, a=a, f=f: c.cx(f, a))
            for s, q, who in acts:
                g = a if who == "a" else f
                layers[s + 2].append(lambda c, g=g, q=q: c.cx(q, g))
            layers.extend([[] for _ in range(max(0, t + 6 - len(layers)))])
            layers[t + 4].append(lambda c, a=a, f=f: c.cx(f, a))
            layers[t + 5].append(lambda c, a=a, f=f: (c.detector(c.measure(a)), c.detector(c.mx(f))))
    # shift so every check ends together is not required; emit in layer order
    layered(c, [l for l in layers if l] , allq)
    return c


if __name__ == "__main__":
    shots = int(float(sys.argv[1])) if len(sys.argv) > 1 else 10**6
    plans = best_plans(n_slots=5)
    for cost, plan in plans[:3]:
        c = build(plan)
        print("tail cost", cost, "n_2q", c.n_2q(), {k[1]: v[0] for k, v in plan.items()})
        evaluate(c.text(), DATA, shots=shots)
