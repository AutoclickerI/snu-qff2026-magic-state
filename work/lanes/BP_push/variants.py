"""New GModel variants seeded from the A1 optimum. Usage: variants.py <variant> <steps> <lmax> <chains> <seed0>"""
import json, multiprocessing as mp, random, sys, time
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/me_layout")
import gmodel as G  # noqa
from verify import load_assign  # noqa

D = {xy: i for i, xy in enumerate(G.DATA0)}
d0, d1, d2, d3, d4, d5, d6 = [D[xy] for xy in G.DATA0]


def variant(name):
    A1 = dict(moves={d1: [(1, 3)]})
    ex = [(1, (2, 3), (2, 2)), (2, (4, 2), (4, 1))]
    xm = {(1, d1): (2, 3), (2, d5): (4, 2)}
    if name == "A1":
        return G.GModel(extras=ex, xmem=xm, **A1)
    if name == "A4":    # + chain extra (3,3) under (2,3), serves d5's tile-1 X
        return G.GModel(extras=ex + [(1, (3, 3), (2, 3))], xmem={**xm, (1, d5): (3, 3)}, **A1)
    if name == "A5":    # A4 but d5's tile-1 X stays on (2,2); (3,3) unused -> skipped
        raise ValueError
    if name == "A6":    # + extra (4,2) also for d4? (4,2) not adjacent to d4; chain (5,1)? skip
        raise ValueError
    raise ValueError(name)


def start(m, base_assign, base_o, rng, lmax):
    for _ in range(300000):
        a = {}
        for k in m.keys:
            a[k] = base_assign.get(k, rng.randint(2, lmax))
        o = list(base_o)
        for k in rng.sample(m.keys, rng.randint(0, 3)):
            if k[0] != "M":
                a[k] = rng.randint(2, lmax)
        if m.cost(a, o) is not None:
            return a, o
    raise RuntimeError("no start")


def job(args):
    name, seed, steps, lmax = args
    m = variant(name)
    cost, a, o, _, _ = json.load(open("/home/jihoon/competitions/quantumn/work/lanes/me_layout/res_A1_9b_1792752451.json"))[0]
    rng = random.Random(seed)
    a0, o0 = start(m, load_assign(a), o, rng, lmax)
    c, A, O = G.anneal(m, a0, o0, seed, steps, lmax, T0=float(__import__("os").environ.get("T0","4e-6")))
    return c, [[list(map(str, k)), v] for k, v in A.items()], O, seed, name


if __name__ == "__main__":
    name, steps, lmax, n, s0 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    with mp.get_context("fork").Pool(n) as p:
        res = p.map(job, [(name, s0 + i, steps, lmax) for i in range(n)])
    res.sort(key=lambda r: r[0])
    for r in res[:6]:
        print(r[0], r[2], r[3], flush=True)
    json.dump(res, open(f"res_{name}_{lmax}_{int(time.time())}.json", "w"))
