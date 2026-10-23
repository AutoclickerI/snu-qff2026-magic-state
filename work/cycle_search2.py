"""Structured search for interleaved superdense cycle orderings (see cycle_interleave.py).

Step 1: per tile, which orders of each ancilla's ops (its data's X- and Z-CNOTs) are valid when
the tile is measured alone.  Step 2: backtrack layer assignments (layers 2..LMAX) using only those
per-ancilla orders, no qubit twice in a layer; keep full-cycle-valid ones with the lowest tail.
"""
import itertools
import pickle
import sys

import cycle_interleave as ci

LMAX = int(sys.argv[1]) if len(sys.argv) > 1 else 7


def tile_valid(t, order_m, order_n):
    """order_*: sequence of (d, typ) for that ancilla; build layers sequentially, other tiles
    measured in a fixed standard way far away (we only test this tile's correctness by
    giving other tiles' ops no presence: validity check includes all tiles' detectors, so place
    the other tiles in standard Z-first order at later layers)."""
    assign = {}
    L = 2
    for (d, typ) in order_m:
        assign[(t, d, typ)] = L; L += 1
    L = 2
    for (d, typ) in order_n:
        assign[(t, d, typ)] = L; L += 1
    base = 10
    for u in range(3):
        if u == t:
            continue
        m = ci.TILES[u][0]
        for anc in (m, (m[0] + 1, m[1])):
            ds = [d for d in ci.TILES[u][1] if ci.ancilla_of(m, d) == anc]
            LL = base
            for typ in "ZX":
                for d in ds:
                    assign[(u, d, typ)] = LL; LL += 1
        base += 8
    return ci.valid(assign, base + 8)


def per_tile_orders():
    out = {}
    for t, (m, ds) in enumerate(ci.TILES):
        n = (m[0] + 1, m[1])
        dm = [d for d in ds if ci.ancilla_of(m, d) == m]
        dn = [d for d in ds if ci.ancilla_of(m, d) == n]
        opts_m = list(itertools.permutations([(d, typ) for d in dm for typ in "XZ"]))
        opts_n = list(itertools.permutations([(d, typ) for d in dn for typ in "XZ"]))
        good = []
        for om in opts_m:
            for on in opts_n:
                if tile_valid(t, om, on):
                    good.append((om, on))
        out[t] = good
        print(f"tile {t}: {len(good)} valid (order_m, order_n) of {len(opts_m) * len(opts_n)}", flush=True)
    return out


def schedule_search(orders, lmax):
    """Assign each ancilla's ordered ops to strictly increasing layers in 2..lmax, no data or
    ancilla used twice per layer. Enumerate exhaustively per combination of tile orders."""
    results = []
    tiles = list(range(3))
    import random
    for combo in itertools.product(*[orders[t] for t in tiles]):
        # sequences: list of (anc, [(t, d, typ), ...])
        seqs = []
        for t, (om, on) in zip(tiles, combo):
            m = ci.TILES[t][0]
            seqs.append((m, [(t, d, typ) for d, typ in om]))
            seqs.append(((m[0] + 1, m[1]), [(t, d, typ) for d, typ in on]))
        # backtracking over layers: place ops layer by layer greedily-late (ALAP from lmax down)
        best = [None, None]

        def rec(idx, assign, used):
            if idx == len(seqs):
                cost = ci.tail_cost(assign, lmax)
                if best[0] is None or cost < best[0]:
                    best[0], best[1] = cost, dict(assign)
                return
            anc, ops = seqs[idx]
            k = len(ops)
            # choose increasing layers for this ancilla's ops
            for layers in itertools.combinations(range(2, lmax + 1), k):
                ok = True
                for (t, d, typ), L in zip(ops, layers):
                    if (L, d) in used:
                        ok = False
                        break
                if not ok:
                    continue
                for (t, d, typ), L in zip(ops, layers):
                    assign[(t, d, typ)] = L
                    used.add((L, d))
                rec(idx + 1, assign, used)
                for (t, d, typ), L in zip(ops, layers):
                    del assign[(t, d, typ)]
                    used.discard((L, d))

        rec(0, {}, set())
        if best[1] is not None:
            results.append(best)
    results.sort(key=lambda r: r[0])
    return results


if __name__ == "__main__":
    orders = per_tile_orders()
    res = schedule_search(orders, LMAX)
    print(len(res), "combos schedulable; best tails", [r[0] for r in res[:12]], flush=True)
    valid = []
    for cost, a in res:
        if ci.valid(a, LMAX):
            valid.append((cost, a))
        if len(valid) >= 60:
            break
    print(len(valid), "fully valid; tails", [v[0] for v in valid[:20]])
    pickle.dump(valid, open(f"interleave2_l{LMAX}.pkl", "wb"))
