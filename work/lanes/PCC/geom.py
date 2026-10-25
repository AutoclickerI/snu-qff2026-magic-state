"""Stage-2 routing pre-check on v36h's round: which C sites can have a free grid partner at the readout tick (old 45)?
Fixed: data D and A cells (prefix/round layout).  Free to move: each B_i (must neighbour D_i for B->D) and each C_i (must
neighbour B_i for B->C); all B are busy at 45 (B->D), all D busy (B->D), A cells busy at 45 except A16 (its v36h job at
45 is the C17 copy).  A support site needs a distinct free partner adjacent to its C cell at 45 (the check CX)."""
import itertools, json
D = [0, 20, 7, 10, 3, 22, 21]; A = [1, 14, 8, 9, 2, 16, 15]
Bv = [6, 26, 13, 11, 4, 23, 27]; Cv = [12, 25, 19, 17, 5, 29, 28]
def nb(q):
    r, c = divmod(q, 6)
    return [rr * 6 + cc for rr, cc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)) if 0 <= rr < 6 and 0 <= cc < 6]
GEN = [0b1010101, 0b1100110, 0b1111000]
C2 = sorted({a ^ b ^ c for a in (0, GEN[0]) for b in (0, GEN[1]) for c in (0, GEN[2])})
busyA = set(A) - {16}
res = {}
# all placements of B (adjacent to its D) and C (adjacent to its B), distinct cells, not on D or A
bopts = [[x for x in nb(D[i]) if x not in D and x not in A] for i in range(7)]
cnt = 0
feasible_sites = [set() for _ in range(7)]
best = {}
for bs in itertools.product(*bopts):
    if len(set(bs)) < 7:
        continue
    copts = [[x for x in nb(bs[i]) if x not in D and x not in A and x not in bs] for i in range(7)]
    for cs in itertools.product(*copts):
        if len(set(cs)) < 7:
            continue
        cnt += 1
        occ = set(D) | busyA | set(bs) | set(cs)
        free = {i: [x for x in nb(cs[i]) if x not in occ] for i in range(7)}
        for i in range(7):
            if free[i]:
                feasible_sites[i].add((bs, cs))
        for w in C2:
            if not w:
                continue
            sup = [i for i in range(7) if w >> i & 1]
            # distinct partners (matching)
            ok = any(len(set(p)) == len(p) for p in itertools.product(*[free[i] for i in sup])) if all(free[i] for i in sup) else False
            if ok:
                best.setdefault(w, []).append((bs, cs))
print('B/C placements enumerated:', cnt)
print('v36h placement in set:', any(bs == tuple(Bv) for bs in itertools.product(*bopts)))
for i in range(7):
    print(f'site {i} (v36h C{Cv[i]}, B{Bv[i]}, D{D[i]}): B options {bopts[i]}, placements with a free partner: {len(feasible_sites[i])}')
for w in C2[1:]:
    print(f'w={w:3d} supp={[i for i in range(7) if w >> i & 1]}: placements with distinct free partners for all sites: {len(best.get(w, []))}',
          (best[w][0] if best.get(w) else ''))
