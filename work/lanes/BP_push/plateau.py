"""Random walk on the proxy plateau around a start schedule; collect every distinct (assign, orient) with
proxy <= thr. Usage: plateau.py <res json> <idx> <thr rel> <steps> <chains> <seed0> <out json>"""
import json, multiprocessing as mp, random, sys
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/me_layout")
import run_moves as R  # noqa
from verify import load_assign  # noqa


def key(a, o):
    return json.dumps([sorted((str(k), v) for k, v in a.items()), list(o)])


def walk(args):
    f, idx, rel, steps, seed, lmax = args
    cost, a, o, _, name = json.load(open(f))[idx]
    m = R.variant(name)
    A, O = load_assign(a), list(o)
    thr = cost * (1 + rel)
    rng = random.Random(seed)
    cur = m.cost(A, O)
    found = {key(A, O): (cur, A, O)}
    for s in range(steps):
        a2, o2 = dict(A), list(O)
        r = rng.random()
        if r < 0.05:
            o2[rng.randrange(3)] ^= 1
        elif r < 0.4:
            k = rng.choice(m.keys)
            if k[0] == "M":
                continue
            a2[k] = rng.randint(2, lmax)
        elif r < 0.65:
            k1, k2 = rng.sample(m.keys, 2)
            if k1[0] == "M" or k2[0] == "M":
                continue
            a2[k1], a2[k2] = a2[k2], a2[k1]
        else:
            k = rng.choice(m.keys)
            if k[0] == "M":
                continue
            old, L = a2[k], rng.randint(2, lmax)
            qs = set(m.qubits_of(k, o2))
            for k2, L2 in list(a2.items()):
                if k2 != k and L2 == L and qs & set(m.qubits_of(k2, o2)):
                    a2[k2] = old
            a2[k] = L
        c2 = m.cost(a2, o2)
        if c2 is None or c2 > thr:
            continue
        A, O, cur = a2, o2, c2
        found.setdefault(key(A, O), (c2, A, O))
    return [(c, [[list(map(str, k)), v] for k, v in a.items()], o, name) for c, a, o in found.values()]


if __name__ == "__main__":
    f, idx, rel, steps, n, s0, out = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]), int(sys.argv[6]), sys.argv[7]
    lmax = int(sys.argv[8]) if len(sys.argv) > 8 else 8
    with mp.get_context("fork").Pool(n) as p:
        res = p.map(walk, [(f, idx, rel, steps, s0 + i, lmax) for i in range(n)])
    allr = {}
    for r in res:
        for c, a, o, name in r:
            allr[json.dumps([sorted(map(str, a)), o])] = (c, a, o, 0, name)
    out_l = sorted(allr.values(), key=lambda r: r[0])
    json.dump(out_l, open(out, "w"))
    print(len(out_l), [round(r[0] * 1e4, 4) for r in out_l[:5]], round(out_l[-1][0] * 1e4, 4))
