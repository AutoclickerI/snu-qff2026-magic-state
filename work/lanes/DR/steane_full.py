"""Full circuit: v11's pre-stage (QASM lines 1..204) + data moves + Steane-type final round on the grid.

Round (steane.py): step T: CX d_i->a_i and CX b_i->c_i; step T+1: read A and C (Z), CX b_i->d_i;
step T+2: read B (X). Blocks are prepared by synth.py circuits (preps json: per block the CX layers
and pivot cells), one block after another, each cell reset just before its first use.

    python steane_full.py <preps.json> <out stem> [order of block preps, default abc]
"""
import json
import sys

PREFIX = "/home/jihoon/competitions/quantumn/work/submissions/v11_A1i_alap45.qasm"
CUT = 204                      # last pre-stage line (its final barrier)
GENS = [[0, 2, 4, 6], [1, 2, 5, 6], [3, 4, 5, 6]]
LAYOUTS = {
    # steane_layout.solve(prefer=PRE_DATA): fewest data moves (3 hops)
    "L1": {'d': [0, 20, 19, 4, 3, 16, 8], 'a': [1, 21, 25, 10, 2, 17, 14], 'b': [6, 26, 18, 5, 9, 22, 7],
           'c': [12, 32, 24, 11, 15, 23, 13]},
    # steane_layout.solve(prefer=PRE_DATA, via_free=True): every block connected through free cells (10 hops)
    "L2": {'d': [6, 32, 7, 5, 9, 35, 8], 'a': [0, 33, 1, 4, 3, 34, 2], 'b': [12, 26, 13, 11, 15, 29, 14],
           'c': [18, 25, 19, 17, 21, 23, 20]},
    # steane_layout2.solve(w_h=1): A and B+C each connected by their own cells (parallel preps), 6 hops
    "L5": {'d': [0, 20, 7, 10, 3, 22, 21], 'a': [1, 14, 8, 9, 2, 16, 15], 'b': [6, 26, 13, 11, 4, 23, 27],
           'c': [12, 25, 19, 17, 5, 29, 28]},
}
LAY = LAYOUTS["L1"]
PRE_DATA = [0, 20, 7, 4, 3, 15, 8]
MOVES = {"L1": [[7, 13, 19], [15, 16]],     # data paths (pre-stage cell first)
         "L2": [[0, 6], [20, 26, 32], [4, 5], [3, 9], [15, 16, 22, 28, 34, 35]],
         "L5": [[4, 10], [15, 16, 22], [8, 9, 15, 21]]}
PRE_DETECTORS = ["c[0]", "c[1]", "c[2]", "c[3]", "c[4]", "c[5]", "c[6]", "c[7]", "c[8]", "c[9]",
                 "c[10] c[7]", "c[11]", "c[12]", "c[13]"]


def build(preps, order="abc", lay=LAY, moves=MOVES["L1"]):
    lines = open(PREFIX).read().split("\n")[:CUT]
    head = [l for l in lines if l.startswith(("OPENQASM", "include", "qreg"))]
    body = [l for l in lines if not l.startswith(("OPENQASM", "include", "qreg", "creg"))]
    layers = []                           # list of lists of qasm statements
    marks = {}                            # layer index -> region name starting there

    def layer():
        layers.append([])
        return layers[-1]
    marks[0] = "moves"
    # data moves: reset the destination, CX src->dst, CX dst->src (src left in |0>)
    hops = [list(zip(p, p[1:])) for p in moves]
    for h in range(max(map(len, hops))):
        r, a, b = layer(), layer(), layer()
        for path in hops:
            if h < len(path):
                s, d = path[h]
                r.append(f"reset q[{d}];")
                a.append(f"cx q[{s}],q[{d}];")
                b.append(f"cx q[{d}],q[{s}];")
    # block preparations, one block after another
    for k in order:
        marks[len(layers)] = f"prep_{k}"
        ops, piv = preps[k]["ops"], preps[k]["pivots"]
        first = {}
        for t, l in enumerate(ops):
            for u, v in l:
                first.setdefault(u, t)
                first.setdefault(v, t)
        for q in lay[k]:
            first.setdefault(q, 0)
        base = len(layers)
        for _ in range(len(ops) + 1):
            layer()
        for q, t in first.items():
            layers[base + t] += [f"reset q[{q}];"] + ([f"h q[{q}];"] if q in piv else [])
        for t, l in enumerate(ops):
            layers[base + 1 + t] += [f"cx q[{u}],q[{v}];" for u, v in l]
    bits = {}
    n = 14
    a, b, c, d = lay['a'], lay['b'], lay['c'], lay['d']
    marks[len(layers)] = "round"
    l1, l2, l3 = layer(), layer(), layer()
    for i in range(7):
        l1 += [f"cx q[{d[i]}],q[{a[i]}];", f"cx q[{b[i]}],q[{c[i]}];"]
    for i in range(7):
        bits[('a', i)] = n; l2.append(f"measure q[{a[i]}] -> c[{n}];"); n += 1
    for i in range(7):
        bits[('c', i)] = n; l2.append(f"measure q[{c[i]}] -> c[{n}];"); n += 1
    for i in range(7):
        l2.append(f"cx q[{b[i]}],q[{d[i]}];")
    for i in range(7):
        bits[('b', i)] = n; l3 += [f"h q[{b[i]}];", f"measure q[{b[i]}] -> c[{n}];"]; n += 1
    used = sorted({int(x.split("[")[1].split("]")[0]) for L in layers for s in L for x in s.split(",") if "q[" in x}
                  | set(PRE_DATA) | set(d))
    bar = "barrier " + ",".join(f"q[{q}]" for q in used) + ";"
    out = head + [f"creg c[{n}];"] + body
    for t, L in enumerate(layers):
        if t in marks:
            out.append(f"// region {marks[t]}")
        if L:
            out += L + [bar]
    out = out[:-1]
    dets = list(PRE_DETECTORS)
    for k in "abc":
        for S in GENS:
            dets.append(" ".join(f"c[{bits[(k, i)]}]" for i in S))
    dets.append(" ".join(f"c[{bits[('c', i)]}]" for i in range(7)))
    out += [f"// DETECTOR {x}" for x in dets]
    return "\n".join(out) + "\n", d


if __name__ == "__main__":
    import os
    name = os.environ.get("LAYOUT", "L1")
    order = sys.argv[3] if len(sys.argv) > 3 else "abc"
    if sys.argv[1].endswith(".json"):
        preps = json.load(open(sys.argv[1]))
    else:                                 # prefix of per-block files <prefix>_<block>.json
        preps = {k: json.load(open(f"{sys.argv[1]}_{k}.json")) for k in "abc"}
    text, data = build(preps, order, LAYOUTS[name], MOVES[name])
    open(sys.argv[2] + ".qasm", "w").write(text)
    json.dump({"data_qubits": data, "source": f"steane_full.py {sys.argv[1]} {order}"}, open(sys.argv[2] + ".json", "w"))
    print(sys.argv[2], "written")
