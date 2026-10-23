"""Anneal (assign, orient, bell layers) on the A1 model. Usage: anneal2.py <steps> <lmax> <chains> <seed0> <T0> [out]"""
import json, multiprocessing as mp, random, sys, time, os
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/me_layout")
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/BP_push")
import gmodel2 as G
import run_moves as R
from verify import load_assign

def model(name="A1"):
    m = R.variant(name); m.__class__ = G.GModel; return m

def feas(m, A, o, bl):
    if not m.feasible(A, o): return False
    for t, (a, b) in enumerate(G.BELL):
        l = bl[t]
        for k, L in A.items():
            qs = set(m.qubits_of(k, o))
            if (a in qs or b in qs) and L <= l: return False
    return True

def cost(m, A, o, bl):
    if not feas(m, A, o, bl): return None
    m.bell_layer = {t: bl[t] for t in range(3)}
    try: return m.proxy(A, o)
    except Exception: return None

def anneal(m, A, o, bl, seed, steps, lmax, T0, T1=2e-7):
    rng = random.Random(seed)
    A, o, bl = dict(A), list(o), list(bl)
    cur = cost(m, A, o, bl); best = (cur, dict(A), list(o), list(bl))
    for s in range(steps):
        T = T0 * (T1 / T0) ** (s / steps)
        a2, o2, b2 = dict(A), list(o), list(bl)
        r = rng.random()
        if r < 0.06: o2[rng.randrange(3)] ^= 1
        elif r < 0.12: b2[rng.randrange(3)] = rng.randint(1, 5)
        elif r < 0.4:
            k = rng.choice(m.keys)
            if k[0] == "M": continue
            a2[k] = rng.randint(2, lmax)
        elif r < 0.6:
            k1, k2 = rng.sample(m.keys, 2)
            if k1[0] == "M" or k2[0] == "M": continue
            a2[k1], a2[k2] = a2[k2], a2[k1]
        else:
            k = rng.choice(m.keys)
            if k[0] == "M": continue
            old, L = a2[k], rng.randint(2, lmax)
            qs = set(m.qubits_of(k, o2))
            for k2, L2 in list(a2.items()):
                if k2 != k and L2 == L and qs & set(m.qubits_of(k2, o2)): a2[k2] = old
            a2[k] = L
        c2 = cost(m, a2, o2, b2)
        if c2 is None: continue
        if c2 < cur or rng.random() < pow(2.718281828, -(c2 - cur) / T):
            A, o, bl, cur = a2, o2, b2, c2
            if cur < best[0]: best = (cur, dict(A), list(o), list(bl))
    return best

def job(args):
    seed, steps, lmax, T0 = args
    name = os.environ.get("VAR", "A1")
    m = model(name)
    cost0, a, o, _, _ = json.load(open("/home/jihoon/competitions/quantumn/work/lanes/me_layout/res_A1_9b_1792752451.json"))[0]
    A = load_assign(a)
    bl0 = [2, 1, 1]
    if name != "A1":
        rng = random.Random(seed)
        base = {k: A.get(k, 0) for k in m.keys}
        for _ in range(200000):
            a2 = {k: (A[k] if k in A else rng.randint(2, lmax)) for k in m.keys}
            for k in m.keys:
                if k[0] == "M": a2[k] = A.get(k, 2 + k[2])
            if cost(m, a2, o, bl0) is not None: A = a2; break
    c, A, o, bl = anneal(m, A, o, bl0, seed, steps, lmax, T0)
    return c, [[list(map(str, k)), v] for k, v in A.items()], o, bl, seed

if __name__ == "__main__":
    steps, lmax, n, s0, T0 = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), float(sys.argv[5])
    with mp.get_context("fork").Pool(n) as p:
        res = p.map(job, [(s0 + i, steps, lmax, T0) for i in range(n)])
    res.sort(key=lambda r: r[0])
    for r in res[:6]: print(r[0], r[2], r[3], r[4], flush=True)
    json.dump(res, open(f"res2_{os.environ.get("VAR","A1")}_{lmax}_{s0}_{int(time.time())}.json", "w"))
