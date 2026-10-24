#!/usr/bin/env python
"""Exact 1-F of an interleaved circuit with the judge's noise switched off by region.

    regions.py <stem> [--procs N] [--only]

Regions per native operation: pre (units listed in <stem>.json prefix_unit_indices), round (other units at
native step >= R from the json), hop (CXs moving a data token: two CXs on one pair, one end holding the token),
A / BC (remaining units inside the A or B+C cells), other. An idle gap belongs to the operation that ends it.
Rows: all, then each region noiseless (or, with --only, the only noisy one).
"""
import argparse
import json
import os
import re
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [os.path.join(HERE, "..", "SCHED"), os.path.join(HERE, "..", "EVAL"), os.path.join(HERE, "..", "TREP")]
import exact2  # noqa: E402
import model  # noqa: E402
import schedule as S  # noqa: E402
from util import native_times  # noqa: E402

A_CELLS = {1, 14, 8, 9, 2, 16, 15}
BC_CELLS = {6, 26, 13, 11, 4, 23, 27, 12, 25, 19, 17, 5, 29, 28}
REGIONS = ("pre", "A", "BC", "hop", "round", "other")
_orig = model.noise_blocks


def unit_regions(units, times, meta):
    pre = set(meta["prefix_unit_indices"])
    tokens = set(json.load(open(meta["_stem"] + ".json")).get("pre_data", [0, 20, 7, 4, 3, 15, 8]))
    seen = {}
    reg = [None] * len(units)
    for i in sorted(range(len(units)), key=lambda k: times[k]):
        u = units[i]
        if i in pre:
            reg[i] = "pre"
        elif times[i] >= meta["R"]:
            reg[i] = "round"
        elif u.name == "CX" and len(set(u.qs) & tokens) == 1:
            reg[i] = "hop"
            pair = frozenset(u.qs)
            seen[pair] = seen.get(pair, 0) + 1
            if seen[pair] == 2:
                tokens ^= set(u.qs)
        elif set(u.qs) <= A_CELLS:
            reg[i] = "A"
        elif set(u.qs) <= BC_CELLS:
            reg[i] = "BC"
        else:
            reg[i] = "other"
    return reg


def patch(text, units, reg, keep):
    converted, clabels, errs = model.convert(text, 36, model.STANDARD)
    assert not errs, errs
    qmap = S.native_qasm_index(text)
    raw_to_unit = {j: i for i, u in enumerate(units) for j in u.raw_indices}

    def nb(stim_text, p, noise, first_order=False):
        prog, blocks = _orig(stim_text, p, noise, first_order)
        _, steps, gaps = model.schedule(stim_text)
        own = {}
        for i, ins in enumerate(prog):
            m = re.match(r"instruction (\d+)", clabels[ins.line_no - 1])
            own[i] = reg[raw_to_unit[qmap[int(m.group(1))]]] if m and int(m.group(1)) in qmap else "other"
            if not keep(own[i]):
                block = blocks[i]
                k = block.index(ins.text)
                n_idle = sum(g[0] == i for g in gaps)
                for j in range(len(block) - n_idle):
                    if j != k:
                        block[j] = re.sub(r"\(([^)]*)\)", "(0)", block[j], count=1)
        for i, q, first, n in gaps:
            if not keep(own[i]):
                blk = blocks[i]
                for j in range(len(blk) - 1, -1, -1):
                    if blk[j].startswith("DEPOLARIZE1(") and blk[j].split()[-1] == str(q) and "(0)" not in blk[j]:
                        blk[j] = re.sub(r"\(([^)]*)\)", "(0)", blk[j], count=1)
                        break
        return prog, blocks
    return nb


def score(text, data, procs):
    ev = exact2.Eval(text, data)
    r = exact2.run(ev, procs, third=True)
    t3 = exact2.third_order(ev, procs)[0] + r["t3bc"] if abs(r["loss1"]) < 1e-12 else float("nan")
    return r["loss"], t3, r["A1"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stem")
    ap.add_argument("--procs", type=int, default=16)
    ap.add_argument("--only", action="store_true")
    a = ap.parse_args()
    text = open(a.stem + ".qasm").read()
    meta = json.load(open(a.stem + ".json"))
    meta["_stem"] = a.stem
    head, raw, tail = S.qasm_ops(text)
    units = S.fold_units(raw)
    times = native_times(text, units)
    reg = unit_regions(units, times, meta)
    print("units by region:", {r: reg.count(r) for r in REGIONS}, flush=True)
    rows = [("all", lambda r: True)]
    for g in REGIONS:
        if g in reg:
            rows.append((("only " if a.only else "no ") + g, (lambda r, g=g: r == g) if a.only else (lambda r, g=g: r != g)))
    base = None
    for name, keep in rows:
        model.noise_blocks = patch(text, units, reg, keep)
        try:
            l2, l3, A1 = score(text, meta["data_qubits"], a.procs)
        finally:
            model.noise_blocks = _orig
        tot = l2 + l3
        base = tot if base is None else base
        print(f"{name:10s} 2nd {l2:.4e}  3rd {l3:.4e}  total {tot:.4e}  ({100 * (tot - base) / base:+6.1f}%)  "
              f"exp(-A1) {exact2.np.exp(-A1):.4f}", flush=True)


if __name__ == "__main__":
    main()
