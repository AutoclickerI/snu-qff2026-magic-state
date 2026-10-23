"""CP-SAT feasible start -> gmodel anneal, per chain. Usage: python l2run.py <variant> <steps> <lmax> <chains> <seed0>
Writes res_<variant>_<lmax>_<seed0>.json in run_moves' result format (cost, assign, orient, seed, name)."""
import json
import multiprocessing as mp
import sys
import time

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/L2_layout_cpsat")
import l2model as L  # noqa: E402


def job(args):
    name, seed, steps, lmax = args
    m = L.variant(name)
    t0 = time.time()
    ok, n = L.starts(m, lmax, 3, seed, tries=4, per=25, seconds=20)
    if not ok:
        return None, [], [0, 0, 0], seed, name, f"no start ({n} tried)"
    pick = ok[(seed % len(ok))] if seed % 2 else ok[0]
    c0 = pick[0]
    c, a, o = L.G.anneal(m, pick[1], pick[2], seed, steps, lmax)
    info = f"start {c0:.4e} ({len(ok)}/{n} valid) {time.time() - t0:.0f}s"
    return c, [[list(map(str, k)), v] for k, v in a.items()], o, seed, name, info


if __name__ == "__main__":
    name, steps, lmax, n, seed0 = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
    with mp.get_context("fork").Pool(n) as p:
        res = p.map(job, [(name, seed0 + s, steps, lmax) for s in range(n)])
    res = [r for r in res if r[0] is not None] + [r for r in res if r[0] is None]
    good = sorted([r for r in res if r[0] is not None], key=lambda r: r[0])
    for r in good[:5]:
        print(name, lmax, f"{r[0]:.6e}", r[2], r[3], r[5], flush=True)
    for r in res:
        if r[0] is None:
            print(name, lmax, "FAILED", r[3], r[5], flush=True)
    json.dump([list(r[:5]) for r in good], open(f"res_{name}_{lmax}_{seed0}.json", "w"))
