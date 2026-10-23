"""Danger of block-A single faults with an ideal logical-X parity check M (undetected = even |Z support on M|)."""
import json, sys
sys.path.insert(0, "/home/jihoon/competitions/quantumn/work/lanes/DR")
import synth
from synth import z_class, x_syndrome
CELLS = [1, 14, 8, 9, 2, 16, 15]
def danger(path, Ms, p=1e-3):
    d = json.load(open(path)); layers_ = d["ops"]; pivots = d["pivots"]; cells = CELLS
    first = {}
    for t, l in enumerate(layers_):
        for u, v in l:
            first.setdefault(u, t); first.setdefault(v, t)
    for q in cells: first.setdefault(q, 0)
    T = len(layers_)
    def prop(z, x, t0):
        z, x = set(z), set(x)
        for l in layers_[t0:]:
            for u, v in l:
                if u in x: x ^= {v}
                if v in z: z ^= {u}
        return z, x
    cnt = {}   # key (frozenset of caught-by) -> weight
    vec = [0.0] * 8
    def rec(zz, xx, w):
        z = zz & set(cells)
        if z_class(z, cells) and not x_syndrome(xx & set(cells), cells):
            # which Z_L Z_j class: remaining z after removing the weight-1 representative
            zi = [cells.index(q) for q in z]
            syn = [i for i in range(7)]
            # identify j: z ^ all-ones has weight <=1
            comp = set(range(7)) - set(zi)
            j = next(iter(comp)) if len(comp) == 1 else (-1 if len(comp) == 0 else None)
            if j is None:   # weight-3 etc: complement of weight-2/3: find j by syndrome
                s = x_syndrome(z, cells); j = s - 1
            vec[0 if j == -1 else 1 + j] += w
            for M in Ms:
                even = len(z & {cells[i] for i in M}) % 2 == 0
                cnt[tuple(M)] = cnt.get(tuple(M), 0) + (w if even else 0)
            cnt["raw"] = cnt.get("raw", 0) + w
    avail = sorted(set(cells) | {q for l in layers_ for e in l for q in e})
    for t, l in enumerate(layers_):
        busy = set()
        for u, v in l:
            busy |= {u, v}
            for pu in "IXYZ":
                for pv in "IXYZ":
                    if pu == pv == "I": continue
                    z = {q for q, P in ((u, pu), (v, pv)) if P in "YZ"}
                    x = {q for q, P in ((u, pu), (v, pv)) if P in "XY"}
                    zz, xx = prop(z, x, t + 1); rec(zz, xx, p / 15)
        for q in avail:
            if q in busy or first.get(q, T) >= t: continue
            last = max((tt for tt, ll in enumerate(layers_) for e in ll if q in e), default=-1)
            if q not in cells and t > last: continue
            for P in "XYZ":
                z = {q} if P in "YZ" else set(); x = {q} if P in "XY" else set()
                zz, xx = prop(z, x, t); rec(zz, xx, p / 3)
    for q in pivots:
        zz, _ = prop({q}, set(), first[q]); rec(zz, set(), p)
    return cnt, [round(v / (p / 15), 2) for v in vec]
if __name__ == "__main__":
    # lines (odd words, detect j not in M) and complements (even words S: detect j in S)
    lines = [[0,1,2],[0,3,4],[0,5,6],[1,3,5],[1,4,6],[2,3,6],[2,4,5]]
    for path in ["../DR/prepA_L5_s7307.json", "../EXENC/prepA_L5_exact.json"]:
        c, v = danger(path, lines)
        print(path, "raw danger", c.pop("raw"), "vector [ZL, ZLZ0..ZLZ6] units p/15:", v)
        for M, val in c.items(): print("  M", M, "residual", val)
