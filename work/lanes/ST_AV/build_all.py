"""layout json (layout_re.py) -> data moves, block preps (SAT synth with helpers), spec, merged circuit.
python build_all.py <layout.json> <stem> [secs per depth] [workers]
"""
import itertools
import json
import sys

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/DR")
import synth  # noqa: E402
from steane_full import GENS  # noqa: E402

PRE = [0, 20, 7, 4, 3, 15, 8]


def bfs(src, dst, blocked):
    from collections import deque
    prev, dq = {src: None}, deque([src])
    while dq:
        u = dq.popleft()
        if u == dst:
            p = []
            while u is not None:
                p.append(u)
                u = prev[u]
            return p[::-1]
        for v in synth.nbrs(u):
            if v not in prev and v not in blocked:
                prev[v] = u
                dq.append(v)
    return None


def plan_moves(final):
    for perm in itertools.permutations(range(7)):
        pos, paths, ok = list(PRE), [], True
        for i in perm:
            if pos[i] == final[i]:
                continue
            others = {pos[j] for j in range(7) if j != i}
            p = bfs(pos[i], final[i], others)
            if p is None:
                ok = False
                break
            paths.append(p)
            pos[i] = final[i]
        if ok:
            return paths
    raise SystemExit("no move order")


def synth_block(cells, kind, avail, secs, workers):
    HAM = GENS + ([[0, 1, 2]] if kind == "plus" else [])
    rows = [{cells[i] for i in r} for r in HAM]
    for depth in range(4, 20):
        r = synth.synth_cells(rows, avail, depth, seconds=secs, workers=workers)
        if r:
            ops, piv, st = r
            print(f"  depth {depth} {st} cx {sum(map(len, ops))} layers {len(ops)}", flush=True)
            return {"ops": ops, "pivots": piv}
        print(f"  depth {depth} none", flush=True)
    raise SystemExit("synth failed")


if __name__ == "__main__":
    lay = json.load(open(sys.argv[1]))
    stem = sys.argv[2]
    secs = int(sys.argv[3]) if len(sys.argv) > 3 else 120
    workers = int(sys.argv[4]) if len(sys.argv) > 4 else 16
    order = "ae" + lay["rest"]
    moves = plan_moves(lay["d"])
    print("moves", moves)
    preps = {}
    for k, kind in (("a", "plus"), ("e", "plus"), ("b", "zero"), ("c", "zero")):
        name = k
        print("block", k, flush=True)
        # block e shares its cells with c (or b): helpers listed under 'e'
        avail = sorted(set(lay[k]) | set(lay["helpers"][k]))
        preps[k] = synth_block(lay[k], kind, avail, secs, workers)
        f = f"{stem}_prep_{k}.json"
        json.dump(preps[k], open(f, "w"))
    spec = {k: lay[k] for k in "dabce"}
    spec.update(moves=moves, order=order, preps={k: f"{stem}_prep_{k}.json" for k in preps})
    json.dump(spec, open(f"{stem}_spec.json", "w"))
    print("spec written")
