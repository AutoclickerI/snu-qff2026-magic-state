"""Base-transfer search: CP-SAT repair of incumbent schedules (all layouts) onto a target layout, then
gmodel anneal from each repaired start. Usage: python l2seed.py <variant> <steps> <lmax> <procs> <seed0> [nbases]"""
import json
import multiprocessing as mp
import sys
import time

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/L2_layout_cpsat")
import l2model as L  # noqa: E402


def job(args):
    name, bi, seed, steps, lmax = args
    m = L.variant(name)
    b = BASES[bi]
    t0 = time.time()
    ok, n = L.repair(m, b[1], b[2], lmax, seconds=20, seed=seed)
    if not ok:
        return None, [], [0, 0, 0], seed, name, f"base {bi} ({b[3]} {b[0]:.4e}): no valid repair ({n})"
    c, a, o = L.G.anneal(m, ok[0][1], ok[0][2], seed, steps, lmax)
    info = f"base {bi} ({b[3]} {b[0]:.4e}) start {ok[0][0]:.4e} {time.time() - t0:.0f}s"
    return c, [[list(map(str, k)), v] for k, v in a.items()], o, seed, name, info


if __name__ == "__main__":
    name, steps, lmax, n, seed0 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    nb = int(sys.argv[6]) if len(sys.argv) > 6 else 6
    BASES = L.bases()
    nb = min(nb, len(BASES))
    jobs = [(name, i % nb, seed0 + i, steps, lmax) for i in range(max(n, nb))]
    with mp.get_context("fork").Pool(n) as p:
        res = p.map(job, jobs)
    good = sorted([r for r in res if r[0] is not None], key=lambda r: r[0])
    for r in good[:6]:
        print(name, lmax, f"{r[0]:.6e}", r[2], r[3], r[5], flush=True)
    for r in res:
        if r[0] is None:
            print(name, lmax, "FAILED", r[3], r[5], flush=True)
    json.dump([list(r[:5]) for r in good], open(f"res_{name}_{lmax}s_{seed0}.json", "w"))
