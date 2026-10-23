"""Exhaustive static enumeration: every data qubit may move up to H hops through sites that are not
(original or final) data; Bell pairs may sit on any 3 disjoint grid edges off the final data sites.
A layout is Z-coverable when every data of tile t is adjacent to a member of Bell pair t (Z parts
need a Bell member, X-only/Z-only extras aside). Prints all Z-coverable layouts."""
import itertools, sys
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/me_layout')
import gmodel as G
H = int(sys.argv[1]) if len(sys.argv) > 1 else 2
GRID = [(x, y) for y in range(6) for x in range(6)]
adj = G.adj
D0 = G.DATA0
def nb(q): return [p for p in GRID if adj(p, q)]
def dests(d):
    out = {D0[d]: 0}
    front = [(D0[d], 0)]
    while front:
        q, h = front.pop()
        if h == H: continue
        for p in nb(q):
            if p in D0 or p in out: continue
            out[p] = h + 1; front.append((p, h + 1))
    return out
opts = [dests(d) for d in range(7)]
edges = [(a, b) for a in GRID for b in GRID if a < b and adj(a, b)]
found = []
for pos in itertools.product(*[sorted(o) for o in opts]):
    if len(set(pos)) < 7: continue
    occ = set(pos)
    cand = []
    for t, ds in enumerate(G.PLAQ):
        cand.append([e for e in edges if not (set(e) & occ) and all(any(adj(m, pos[d]) for m in e) for d in ds)])
    for bells in itertools.product(*cand):
        if len({q for e in bells for q in e}) < 6: continue
        hops = sum(opts[d][pos[d]] for d in range(7))
        found.append((hops, pos, bells))
found.sort()
print('Z-coverable layouts with moves <=', H, 'hops each:', len(found))
for hops, pos, bells in found:
    moved = {d: pos[d] for d in range(7) if pos[d] != D0[d]}
    onold = [q for e in bells for q in e if q in D0]
    print(hops, moved, bells, 'bell-on-vacated' if onold else '')
