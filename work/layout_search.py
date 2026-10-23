"""Search 6x6 placements of the 7 Steane data qubits for grid-friendly gadgets.

A design needs:
  * one connected "gadget" of ancilla sites per plaquette S1,S2,S3 (each plaquette data qubit
    adjacent to some gadget site), gadgets pairwise disjoint so checks can run in parallel;
  * a way to measure X^7 for the logical check: either the data qubits form a connected graph
    (parity tree through the data) or a connected ancilla "W-cat" touching all 7 data.
Cost = total CX of one X+Z round + W-check CX (+ depth proxy). Prints the best designs.
"""

import itertools
import random
import sys
from collections import deque

R = C = 6
SUP = [(0, 2, 4, 6), (1, 2, 5, 6), (3, 4, 5, 6)]


def nb(q):
    r, c = divmod(q, C)
    out = []
    if r > 0: out.append(q - C)
    if r < R - 1: out.append(q + C)
    if c > 0: out.append(q - 1)
    if c < C - 1: out.append(q + 1)
    return out


NB = [nb(q) for q in range(R * C)]


def connected(sites):
    sites = set(sites)
    if not sites:
        return False
    start = next(iter(sites))
    seen, stack = {start}, [start]
    while stack:
        q = stack.pop()
        for n in NB[q]:
            if n in sites and n not in seen:
                seen.add(n)
                stack.append(n)
    return len(seen) == len(sites)


def covers(sites, targets):
    return all(any(n in sites for n in NB[t]) for t in targets)


def connected_subsets(free, seed_sites, max_size):
    """All connected subsets of `free` of size <= max_size containing a site from seed_sites."""
    out = set()
    frontier = {frozenset([s]) for s in seed_sites if s in free}
    out |= frontier
    for _ in range(max_size - 1):
        nxt = set()
        for S in frontier:
            for q in S:
                for n in NB[q]:
                    if n in free and n not in S:
                        nxt.add(S | {n})
        out |= nxt
        frontier = nxt
    return out


def gadget_options(data_pos, plaquette, free, max_size=3):
    targets = [data_pos[i] for i in plaquette]
    seeds = {n for n in NB[targets[0]] if n in free}
    opts = [S for S in connected_subsets(free, seeds, max_size) if covers(S, targets)]
    if not opts:
        return []
    m = min(map(len, opts))
    return [S for S in opts if len(S) <= m + 1]


def _bfs(src, free):
    dist, prev = {src: 0}, {src: None}
    dq = deque([src])
    while dq:
        q = dq.popleft()
        for n in NB[q]:
            if n in free and n not in dist:
                dist[n] = dist[q] + 1
                prev[n] = q
                dq.append(n)
    return dist, prev


def w_cat_size(data_pos, free):
    """Approximate smallest connected ancilla set touching all 7 data: greedy Steiner growth
    (repeatedly attach the uncovered data qubit whose nearest touching site is closest)."""
    best = (None, None)
    for start in {n for t in data_pos for n in NB[t] if n in free}:
        S = {start}
        ok = True
        while not covers(S, data_pos):
            # multi-source BFS from S through free sites
            dist, prev = {}, {}
            dq = deque()
            for q in S:
                dist[q], prev[q] = 0, None
                dq.append(q)
            while dq:
                q = dq.popleft()
                for n in NB[q]:
                    if n in free and n not in dist:
                        dist[n], prev[n] = dist[q] + 1, q
                        dq.append(n)
            todo = [t for t in data_pos if not any(n in S for n in NB[t])]
            cand = [(dist[n], n) for t in todo for n in NB[t] if n in dist]
            if not cand:
                ok = False
                break
            _, n = min(cand)
            while n is not None and n not in S:
                S.add(n)
                n = prev[n]
        if ok and (best[0] is None or len(S) < best[0]):
            best = (len(S), frozenset(S))
    return best


def evaluate(data_pos):
    free = set(range(R * C)) - set(data_pos)
    opts = [gadget_options(data_pos, s, free) for s in SUP]
    if not all(opts):
        return None
    best = None
    for combo in itertools.product(*opts):
        if len(combo[0] | combo[1] | combo[2]) != sum(map(len, combo)):
            continue  # gadgets must be disjoint
        cx_round = sum(2 * (2 * (len(g) - 1) + 4) for g in combo)
        # load on the busiest data qubit within a round (its CX count) is fixed at 6 for d6
        cand = (cx_round, combo)
        if best is None or cand[0] < best[0]:
            best = cand
    if best is None:
        return None
    data_conn = connected(data_pos)
    wsize, wcat = w_cat_size(data_pos, free)
    w_tree_cx = 12 if data_conn else None
    w_cat_cx = (wsize - 1) + 7 if wsize else None
    wcx = min(x for x in (w_tree_cx, w_cat_cx) if x is not None) if (w_tree_cx or w_cat_cx) else None
    if wcx is None:
        return None
    return {"cost": best[0] + wcx, "round_cx": best[0], "gadgets": best[1], "w_cx": wcx,
            "data_conn": data_conn, "wcat": wcat, "data": tuple(data_pos)}


def draw(res):
    grid = [["  ."] * C for _ in range(R)]
    for i, q in enumerate(res["data"]):
        r, c = divmod(q, C)
        grid[r][c] = f" d{i}"
    for k, g in enumerate(res["gadgets"]):
        for q in g:
            r, c = divmod(q, C)
            grid[r][c] = f" g{k + 1}"
    if res["wcat"]:
        for q in res["wcat"]:
            r, c = divmod(q, C)
            if grid[r][c] == "  .":
                grid[r][c] = "  w"
            else:
                grid[r][c] = grid[r][c][:-1] + grid[r][c][-1].upper() if False else grid[r][c] + "*"
    return "\n".join("".join(f"{x:>5}" for x in row) for row in grid)


def anneal(seed, iters=4000):
    rng = random.Random(seed)
    # start: random compact placement in the central 4x4
    centre = [q for q in range(R * C) if 1 <= q // C <= 4 and 1 <= q % C <= 4]
    pos = rng.sample(centre, 7)
    cur = evaluate(pos)
    cur_cost = cur["cost"] if cur else 10**6
    best = (cur_cost, cur)
    T = 6.0
    for it in range(iters):
        new = list(pos)
        if rng.random() < 0.5:
            i = rng.randrange(7)
            choices = [q for q in range(R * C) if q not in new]
            new[i] = rng.choice(choices)
        else:
            i, j = rng.sample(range(7), 2)
            new[i], new[j] = new[j], new[i]
        res = evaluate(new)
        cost = res["cost"] if res else 10**6
        if cost <= cur_cost or rng.random() < pow(2.718, (cur_cost - cost) / T):
            pos, cur_cost = new, cost
            if cost < best[0]:
                best = (cost, res)
        T = max(0.3, T * 0.999)
    return best


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 8
    results = []
    for s in range(n):
        cost, res = anneal(s)
        if res:
            results.append((cost, res))
            print(f"seed {s}: cost {cost} round_cx {res['round_cx']} w_cx {res['w_cx']} "
                  f"data_conn {res['data_conn']} gadget sizes {[len(g) for g in res['gadgets']]}", flush=True)
    results.sort(key=lambda x: x[0])
    seen = set()
    for cost, res in results[:5]:
        if res["data"] in seen:
            continue
        seen.add(res["data"])
        print(f"\ncost {cost}  round_cx {res['round_cx']}  w_cx {res['w_cx']}  data {res['data']}")
        print(draw(res))
