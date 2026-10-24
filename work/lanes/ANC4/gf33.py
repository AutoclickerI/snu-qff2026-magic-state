#!/usr/bin/env python
"""Grid-free price of a Steane round right after the pre-stage (adjacency ignored).

v11's pre-stage (steane_full.PREFIX, data last touched at step 32) followed by blocks prepared in the 21
cells the pre-stage never uses, scheduled to finish just before the round. Variants:
  sep    separate standard 9-CX encoders for A (|+_L>), B (|0_L>), C (|0_L>)
  ver    sep + A verified by a |+_L> block V (CX v->a, V read in X) whose cells C reuses later
  flag   no C: B checked by one ancilla reading Z on a weight-3 logical support S (--flag-set, --enc-order)
Round at R: CX d->a and CX b->c; R+1: read A, C, CX b->d; R+2: read B.

    gf33.py <variant> <R> <out stem> [--vgap k]   (exact score: lanes/EVAL/exact2.py <stem>.qasm --third)
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "EARLY"))
sys.path.insert(0, os.path.join(HERE, "..", "DR"))
import early_merge  # noqa: E402
from steane_full import GENS, PRE_DETECTORS  # noqa: E402

PRE_DATA = [0, 20, 7, 4, 3, 15, 8]
FREE = [5, 11, 12, 16, 17, 18, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]
PIV = [0, 1, 3]
LAYERS0 = [[(0, 2), (1, 6), (3, 5)], [(0, 4), (1, 2), (3, 6)], [(0, 6), (1, 5), (3, 4)]]


def enc(cells, plus, t0):
    """(step, stmt) list: |0_L> (plus=False) or |+_L> (plus=True) on cells, first layer at t0."""
    out = []
    for i, q in enumerate(cells):
        out.append((t0 - 1, f"reset q[{q}];"))
        if (i in PIV) != plus:
            out.append((t0 - 1, f"h q[{q}];"))
    for k, layer in enumerate(LAYERS0):
        for c, t in layer:
            a, b = (cells[t], cells[c]) if plus else (cells[c], cells[t])
            out.append((t0 + k, f"cx q[{a}],q[{b}];"))
    return out


def build(variant, R, vgap, fset=(0, 1, 2), order=(0, 1, 2)):
    head, stmts = early_merge.prefix_steps()
    by = {}
    for s, st in stmts:
        by.setdefault(st, []).append(s)
    d = PRE_DATA
    A, B, C = FREE[0:7], FREE[7:14], FREE[14:21]
    ops = enc(B, False, R - 3) + enc(C, False, R - 3) + enc(A, True, R - 3)
    n = 14
    bits = {}
    extra = []
    if variant == "flag":
        f = C[0]
        lay = [LAYERS0[k] for k in order]
        ops = enc(A, True, R - 3)
        for i, q in enumerate(B):                      # B's encoder at R-5..R-3, flag CXs at R-2..R
            ops.append((R - 6, f"reset q[{q}];"))
            if i in PIV:
                ops.append((R - 6, f"h q[{q}];"))
        for k, layer in enumerate(lay):
            for c, t in layer:
                ops.append((R - 5 + k, f"cx q[{B[c]}],q[{B[t]}];"))
        ops.append((R - 3, f"reset q[{f}];"))
        for k, i in enumerate(fset):
            ops.append((R - 2 + k, f"cx q[{B[i]}],q[{f}];"))
        bits[("f", 0)] = n
        ops.append((R + 1, f"measure q[{f}] -> c[{n}];"))
        n += 1
        extra = ["f"]
    if variant == "ver":
        V = C                                # V lives in C's cells and is read before C is prepared
        tv = R - 3 - vgap                    # V's check step
        ops = enc(B, False, R - 3) + enc(A, True, tv - 4) + enc(V, True, tv - 4)
        ops += [(tv, f"cx q[{V[i]}],q[{A[i]}];") for i in range(7)]
        for i, q in enumerate(V):
            bits[("v", i)] = n
            ops += [(tv + 1, f"h q[{q}];"), (tv + 1, f"measure q[{q}] -> c[{n}];")]
            n += 1
        ops += enc(C, False, R - 3)
        extra = ["v"]
    for t, s in ops:
        by.setdefault(t, []).append(s)
    r0, r1, r2 = [], [], []
    for i in range(7):
        r0 += [f"cx q[{d[i]}],q[{A[i]}];"] + ([] if variant == "flag" else [f"cx q[{B[i]}],q[{C[i]}];"])
    for k, cells in (("a", A),) + ((("c", C),) if variant != "flag" else ()):
        for i, q in enumerate(cells):
            bits[(k, i)] = n
            r1.append(f"measure q[{q}] -> c[{n}];")
            n += 1
    r1 += [f"cx q[{B[i]}],q[{d[i]}];" for i in range(7)]
    for i, q in enumerate(B):
        bits[("b", i)] = n
        r2 += [f"h q[{q}];", f"measure q[{q}] -> c[{n}];"]
        n += 1
    by.setdefault(R, []).extend(r0)
    by.setdefault(R + 1, []).extend(r1)
    by.setdefault(R + 2, []).extend(r2)
    bar = "barrier " + ",".join(f"q[{q}]" for q in range(36)) + ";"
    out = head + [f"creg c[{n}];"]
    for t in range(min(by), R + 3):
        out += by.get(t, []) or ["id q[19];"]     # an empty step still takes time: q19 is measured at 32
        out.append(bar)
    out = out[:-1]
    dets = list(PRE_DETECTORS)
    blocks = ["a", "b"] + ([] if variant == "flag" else ["c"]) + [x for x in extra if x != "f"]
    for k in blocks:
        for S in GENS:
            dets.append(" ".join(f"c[{bits[(k, i)]}]" for i in S))
    for k in ([] if variant == "flag" else ["c"]) + [x for x in extra if x != "f"]:
        dets.append(" ".join(f"c[{bits[(k, i)]}]" for i in range(7)))
    if variant == "flag":
        dets.append(f"c[{bits[('f', 0)]}]")
    out += [f"// DETECTOR {x}" for x in dets]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("variant", choices=["sep", "ver", "flag", "anc4", "direct4", "redundant7"])
    ap.add_argument("--flag-set", default="0,1,2")
    ap.add_argument("--enc-order", default="0,1,2")
    ap.add_argument("R", type=int)
    ap.add_argument("out")
    ap.add_argument("--vgap", type=int, default=2)
    a = ap.parse_args()
    if a.variant in ("anc4", "direct4", "redundant7"):
        from generate import build as build_checker
        text = build_checker(a.variant, a.R)
    else:
        text = build(a.variant, a.R, a.vgap, tuple(map(int, a.flag_set.split(","))), tuple(map(int, a.enc_order.split(","))))
    open(a.out + ".qasm", "w").write(text)
    json.dump({"data_qubits": PRE_DATA, "grid_free": True, "variant": a.variant, "R": a.R}, open(a.out + ".json", "w"))


if __name__ == "__main__":
    main()
