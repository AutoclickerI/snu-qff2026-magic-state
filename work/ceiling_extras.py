"""Ceiling estimate (prototype only, adjacency ignored): every data qubit gets an X-only extra cat
member for its last X-part CNOT, as (1,3)/(4,2) do for d1/d5 in v6. Anneal with the joint proxy."""
import sys
import multiprocessing as mp
import json, time
import qcirc
qcirc.allow_any_coupling()
import gen2_cycle as g2

g2.EXTRAS_ALL.update({
    "i_d0": (0, (0, 5), (1, 0), [(0, 0)]),
    "i_d2": (0, (1, 5), (1, 0), [(1, 1)]),
    "i_d4": (0, (2, 5), (2, 0), [(3, 0)]),
    "i_d6": (0, (3, 5), (2, 0), [(2, 1)]),
    "i_d3": (2, (4, 5), (4, 1), [(4, 0)]),
})

def smart_start(m, seed):
    import random
    rng = random.Random(seed)
    base, o = g2.start_from(g2.Model(["t1c13", "t2c42"]), "gen2_t1c13+t2c42_8_1792739653.json")
    for _ in range(5000):
        a = dict(base)
        for t, c, parent, ds in m.extras:
            if (t, "A", c) in a:
                continue
            for d in ds:
                if rng.random() < 0.5:
                    a[(t, d, "X")] = rng.randint(3, LMAX)
            lx = min(a[(t, d, "X")] for d in ds)
            a[(t, "A", c)] = rng.randint(2, max(2, lx - 1))
        if m.cost(a, o) is not None:
            return a, o
    raise RuntimeError("no start")


def job(seed):
    m = g2.Model(EX)
    a0, o0 = smart_start(m, seed)
    c, a, o = g2.anneal(m, a0, o0, seed, STEPS, LMAX)
    return c, [[list(map(str, k)), v] for k, v in a.items()], o, seed, EX

if __name__ == "__main__":
    EX = sys.argv[1].split(",")
    STEPS, LMAX, N = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    with mp.get_context("fork").Pool(N) as p:
        res = p.map(job, range(700, 700 + N))
    res.sort(key=lambda r: r[0])
    for r in res[:4]:
        print(r[0], r[2], flush=True)
    json.dump(res, open(f"ceiling_{'+'.join(EX)}_{int(time.time())}.json", "w"))
