import sys, json, lay3
from lay3 import *
def stripe_extra(orient, flip, r0, c0, nstripe=5):
    def f(m, x):
        # vertical stripes: column c in c0..c0+4, rows r0..r0+3: a,d,b,c (flip: reversed). orient 1: transpose
        def cell(r, c): return (c*C+r) if orient else (r*C+c)
        order = "adbc" if not flip else "cbda"
        s = [m.NewBoolVar("") for _ in range(7)]
        m.Add(sum(s) == nstripe)
        for i in range(7):
            for k in "dabc":
                for q in range(N):
                    r, c = divmod(q, C)
                    if orient: r, c = c, r
                    inside = (r0 <= r < r0+4 and c0 <= c < c0+nstripe)
                    want = inside and order[r-r0] == k
                    # s_i => position pattern
            for col in range(c0, c0+nstripe):
                pass
            for k_idx, k in enumerate(order):
                m.AddBoolOr([x[(k, i, cell(r0+k_idx, col)) ] for col in range(c0, c0+nstripe)]).OnlyEnforceIf(s[i])
    return f
if __name__ == "__main__":
    orient, flip, r0, c0, secs = map(int, sys.argv[1:6])
    pre = lay3.PRE
    r = solve(pre, 1, secs, 4, 8, stripe_extra(orient, flip, r0, c0))
    json.dump({"cfg": [orient, flip, r0, c0], "pre": pre, "res": r}, open(f"st_{orient}{flip}{r0}{c0}.json", "w"))
