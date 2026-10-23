"""Score many candidates at the official setting in parallel.

Candidates are (label, builder spec) built inside worker processes by `make(spec)`.
"""
import json
import multiprocessing as mp
import sys
import time


def make(spec):
    import cultiv_port as cp
    from qcirc import Circ
    import cycle_opt as co
    kind = spec["kind"]
    if kind == "port":
        c = cp.build(("inject", "check", "cycle"), "Tswap", z_first=spec.get("z_first", True),
                     lockstep=spec.get("lockstep", True))
    elif kind == "cycleperm":
        lay = co.plan(tuple(map(tuple, spec["pf"])), tuple(map(tuple, spec["ps"])), spec["first"])
        c = co.build_with(lay)
    elif kind == "interleave":
        import pickle
        import cycle_interleave as ci
        cost, assign = pickle.load(open(spec["pkl"], "rb"))[spec["idx"]]
        c = ci.build_with(assign, spec["lmax"], lazy=False)
    elif kind == "gen":
        import ast
        import gen_cycle as gc
        res = json.load(open(spec["file"]))
        _, a, o, _ = res[spec["idx"]]
        assign = {(int(k[0]), ast.literal_eval(k[1]) if k[1] != "U" else "U", k[2]): L for k, L in a}
        c = Circ()
        cp.run_chunk(c, cp.extract_chunk("make_chunk_d3_init_unitary", cp.UP + "_injection_stage.py"), s_to="Tswap")
        cp.run_chunk(c, cp.extract_chunk("make_chunk_d3_double_cat_check", cp.UP + "_cultivation_stage.py"), s_to="Tswap")
        gc.emit(c, assign, o)
    elif kind == "gen2":
        import ast
        import gen2_cycle as g2
        r = json.load(open(spec["file"]))[spec["idx"]]
        _, a, o, _, extras = r
        m = g2.Model(extras)
        def key(k):
            t, d, typ = k
            if d in ("U", "A"):
                return (int(t), d, ast.literal_eval(typ) if d == "A" else typ)
            return (int(t), ast.literal_eval(d), typ)
        assign = {key(k): L for k, L in a}
        c = Circ()
        cp.run_chunk(c, cp.extract_chunk("make_chunk_d3_init_unitary", cp.UP + "_injection_stage.py"), s_to="Tswap")
        cp.run_chunk(c, cp.extract_chunk("make_chunk_d3_double_cat_check", cp.UP + "_cultivation_stage.py"), s_to="Tswap")
        m.emit(c, assign, o)
    else:
        raise ValueError(kind)
    if spec.get("lazy"):
        c = c.rescheduled(lazy_init=True)
    return c, cp.DATA


def work(item):
    label, spec, shots = item
    import tprep
    t = time.time()
    c, data = make(spec)
    rep = tprep.check(c.text(), data, shots=shots, seed=0)
    return {"label": label, "spec": spec, "score": rep.score, "sem": rep.sem, "acc": rep.acceptance,
            "n_2q": rep.n_2q, "passed": rep.passed, "sec": round(time.time() - t, 1)}


def run(items, procs=None):
    with mp.get_context("spawn").Pool(procs or min(len(items), 48)) as pool:
        res = pool.map(work, items, chunksize=1)
    res.sort(key=lambda r: (r["score"] if r["passed"] else 1))
    for r in res:
        print(f"{r['label']:40s} 1-F={r['score']:.5g} ± {r['sem']:.2g}  acc={r['acc']:.4f}  2q={r['n_2q']}  "
              f"pass={r['passed']}  {r['sec']}s", flush=True)
    return res


if __name__ == "__main__":
    shots = int(float(sys.argv[1])) if len(sys.argv) > 1 else 10**8
    import itertools
    import cycle_opt as co
    perms = list(itertools.permutations(range(3)))
    cands = []
    for first in ("Z", "X"):
        for pf in itertools.product(perms, repeat=3):
            for ps in itertools.product(perms, repeat=3):
                lay = co.plan(pf, ps, first)
                if lay:
                    cands.append((co.tail_cost(lay), first, pf, ps))
    cands.sort()
    items = [("v2 port lockstep", {"kind": "port"}, shots),
             ("v3 port lockstep lazy", {"kind": "port", "lazy": True}, shots)]
    for i, (cost, first, pf, ps) in enumerate(cands[:20]):
        for lazy in (False, True):
            items.append((f"perm{i} t{cost} {first}{' lazy' if lazy else ''}",
                          {"kind": "cycleperm", "first": first, "pf": pf, "ps": ps, "lazy": lazy}, shots))
    res = run(items)
    json.dump(res, open(f"batch_{int(time.time())}.json", "w"), indent=1)
