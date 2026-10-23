"""Anneal relocation variants from v6's schedule. Usage: python run_moves.py <variant> <steps> <lmax> <chains>"""
import json
import multiprocessing as mp
import pickle
import random
import sys
import time

sys.path.insert(0, ".")
import gmodel as G  # noqa: E402

D = {xy: i for i, xy in enumerate(G.DATA0)}
d1, d5 = D[(2, 3)], D[(3, 2)]


def variant(name):
    if name == "v6":
        return G.GModel(extras=[(1, (1, 3), (1, 2)), (2, (4, 2), (4, 1))], xmem={(1, d1): (1, 3), (2, d5): (4, 2)})
    if name == "A1":   # d1 -> (1,3); vacated (2,3) becomes an X-only member for d1; (4,2) for d5
        return G.GModel(moves={d1: [(1, 3)]}, extras=[(1, (2, 3), (2, 2)), (2, (4, 2), (4, 1))],
                        xmem={(1, d1): (2, 3), (2, d5): (4, 2)})
    if name == "A2":   # d1 -> (1,3); only (4,2)
        return G.GModel(moves={d1: [(1, 3)]}, extras=[(2, (4, 2), (4, 1))], xmem={(2, d5): (4, 2)})
    if name == "A3":   # d1 -> (1,3); no extras
        return G.GModel(moves={d1: [(1, 3)]})
    raise ValueError(name)


def start(model, name, seed, lmax):
    rng = random.Random(seed)
    a6, o6 = pickle.load(open("v6_assign.pkl", "rb"))
    base = {k: L for k, L in a6.items() if k in model.keys}
    for k in model.keys:
        if k[0] == "M":
            base[k] = 2 + k[2]
    for k in model.keys:
        base.setdefault(k, rng.randint(2, lmax))
    if model.cost(base, o6) is not None:
        return base, o6
    for _ in range(200000):
        a = dict(base)
        for k in rng.sample(model.keys, rng.randint(1, 4)):
            if k[0] != "M":
                a[k] = rng.randint(2, lmax)
        o = list(o6) if rng.random() < 0.7 else [rng.randint(0, 1) for _ in range(3)]
        if model.cost(a, o) is not None:
            return a, o
    raise RuntimeError("no start")


def start_from(model, spec, seed, lmax):
    """Map a gen2-format schedule (file:idx) onto this variant's keys, then repair like start()."""
    import ast
    f, idx = spec.rsplit(":", 1)
    _, a, o, *_ = json.load(open(f))[int(idx)]
    rng = random.Random(seed)
    exmap = {t: c for t, c, _ in model.extras}
    base = {}
    for (t, d, typ), L in a:
        t = int(t)
        if d == "U":
            k = (t, "U", "")
        elif d == "A":
            if t not in exmap:
                continue
            k = (t, "A", exmap[t])
        else:
            k = (t, G.DATA0.index(ast.literal_eval(d)), typ)
        if k in model.keys:
            base[k] = L
    for k in model.keys:
        if k[0] == "M":
            base[k] = 2 + k[2]
    for k in model.keys:
        base.setdefault(k, rng.randint(2, lmax))
    if model.cost(base, o) is not None:
        return base, list(o)
    for _ in range(200000):
        a2 = dict(base)
        for k in rng.sample(model.keys, rng.randint(1, 4)):
            if k[0] != "M":
                a2[k] = rng.randint(2, lmax)
        o2 = list(o) if rng.random() < 0.7 else [rng.randint(0, 1) for _ in range(3)]
        if model.cost(a2, o2) is not None:
            return a2, o2
    raise RuntimeError("no start from base")


def job(args):
    name, seed, steps, lmax = args
    m = variant(name)
    import os
    if os.environ.get("BASE"):
        a0, o0 = start_from(m, os.environ["BASE"], seed, lmax)
    elif os.environ.get("RANDSTART"):
        a0, o0 = G.random_start(m, lmax, random.Random(seed))
    else:
        a0, o0 = start(m, name, seed, lmax)
    c, a, o = G.anneal(m, a0, o0, seed, steps, lmax)
    return c, [[list(map(str, k)), v] for k, v in a.items()], o, seed, name


if __name__ == "__main__":
    name, steps, lmax, n = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    with mp.get_context("fork").Pool(n) as p:
        seed0 = int(sys.argv[5]) if len(sys.argv) > 5 else 900
        res = p.map(job, [(name, seed0 + s, steps, lmax) for s in range(n)])
    res.sort(key=lambda r: r[0])
    for r in res[:5]:
        print(r[0], r[2], r[3], flush=True)
    import os
    json.dump(res, open(f"res_{name}_{lmax}{'b' if os.environ.get('BASE') else ('r' if os.environ.get('RANDSTART') else '')}_{int(time.time())}.json", "w"))
