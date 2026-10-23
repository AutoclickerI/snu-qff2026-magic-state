#!/usr/bin/env python
"""Exact 1-F (2nd + 3rd order) of a circuit with the judge's noise switched off in one region at a time.

    ablate.py <circuit.qasm> --pre-end S --round-start R [--a 1,14,...] [--procs 24] [--only | --pairs]

Regions, by the native time step an operation or idle run starts at:
  pre    step <= S;    round  step >= R;
  wait   data idles in between;   moves  operations touching data in between;
  A      other operations (and their idles) on --a cells in between;   prep  everything else in between.
Each row is the exact loss with that region noiseless (--only: with only that region noisy), so the
difference to 'all' prices removing that region's noise. --pairs instead splits the full circuit's
2nd-order loss by region pair (with the largest pair of each) and its weight-3 term by region.
Data qubits come from <circuit>.json.
"""
import argparse
import collections
import json
import os
import re
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "EVAL"))
import exact2  # noqa: E402
import model  # noqa: E402
from tprep.noise import schedule  # noqa: E402

REGIONS = ("pre", "wait", "moves", "A", "prep", "round")
_orig = model.noise_blocks


def labeller(data, a_cells, pre_end, round_start):
    def op(qs, step):
        if step <= pre_end:
            return "pre"
        if step >= round_start:
            return "round"
        if set(qs) & data:
            return "moves"
        return "A" if set(qs) <= a_cells else "prep"

    def idle(q, first, owner):
        if first <= pre_end:
            return "pre"
        if first >= round_start:
            return "round"
        return "wait" if q in data else owner
    return op, idle


def patched(keep, op_region, idle_region):
    def nb(text, p, noise, first_order=False):
        prog, blocks = _orig(text, p, noise, first_order)
        _, steps, gaps = schedule(text)
        own = {}
        for i, (ins, block) in enumerate(zip(prog, blocks)):
            st = min((s for _, s in steps[i]), default=0)
            own[i] = op_region(ins.qubits, st)
            if not keep(own[i]):
                k = block.index(ins.text)
                n_idle = sum(1 for g in gaps if g[0] == i)  # idle lines sit at the block's end
                for j in range(len(block) - n_idle):
                    if j != k:
                        block[j] = re.sub(r"\(([^)]*)\)", "(0)", block[j], count=1)
        for i, q, first, n in gaps:
            if not keep(idle_region(q, first, own[i])):
                blk = blocks[i]
                for j in range(len(blk) - 1, -1, -1):
                    if blk[j].startswith("DEPOLARIZE1(") and blk[j].split()[-1] == str(q) and "(0)" not in blk[j]:
                        blk[j] = re.sub(r"\(([^)]*)\)", "(0)", blk[j], count=1)
                        break
        return prog, blocks
    return nb


def pairs(text, data, op_region, idle_region, procs):
    ev = exact2.Eval(text, data)
    reg = {}
    for c, ch in enumerate(ev.m.chans):
        lab = ev.chan_label(c)
        st = int(str(lab["steps"]).split("..")[0])
        if ch["gap"] is not None:
            reg[c] = idle_region(lab["qubits"][0], st, op_region(lab["qubits"], st))
        else:
            reg[c] = op_region(lab["qubits"], st)
    r = exact2.run(ev, procs, keep_thr=0.0)
    m, top = collections.Counter(), {}
    for c, i, j, nij, aab in r["big"]:
        k = "x".join(sorted((reg[int(ev.fch[i])], reg[int(ev.fch[j])])))
        m[k] += c
        if c > top.get(k, (0,))[0]:
            top[k] = (c, ev.fault_label(i), ev.fault_label(j))
    print(f"2nd order {r['loss2']:.4e} by region pair:")
    for k, v in m.most_common():
        print(f"  {k:14s} {v:.3e} {100 * v / r['loss2']:5.1f}%   e.g. {top[k][1]} + {top[k][2]}")
    t3, big3 = exact2.third_order(ev, procs)
    per = collections.Counter()
    for v, *ijk in big3:
        for x in ijk:
            per[reg[int(ev.fch[x])]] += v / 3
    kept = sum(per.values())
    print(f"weight-3 term {t3:.4e} by region (each triple split in thirds; kept triples cover {kept:.4e}):")
    for k, v in per.most_common():
        print(f"  {k:8s} {v:.3e} {100 * v / kept:5.1f}%")


def score(text, data, procs):
    ev = exact2.Eval(text, data)
    r = exact2.run(ev, procs, third=True)
    t3 = exact2.third_order(ev, procs)[0] + r["t3bc"] if abs(r["loss1"]) < 1e-12 else float("nan")
    return r["loss1"], r["loss"], t3, r["A1"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("qasm")
    ap.add_argument("--pre-end", type=int, required=True)
    ap.add_argument("--round-start", type=int, required=True)
    ap.add_argument("--a", default="")
    ap.add_argument("--procs", type=int, default=24)
    ap.add_argument("--only", action="store_true")
    ap.add_argument("--pairs", action="store_true")
    a = ap.parse_args()
    text = open(a.qasm).read()
    data = json.load(open(a.qasm.rsplit(".", 1)[0] + ".json"))["data_qubits"]
    a_cells = {int(x) for x in a.a.split(",") if x}
    op_region, idle_region = labeller(set(data), a_cells, a.pre_end, a.round_start)
    if a.pairs:
        return pairs(text, data, op_region, idle_region, a.procs)
    rows = [("all", lambda r: True)]
    for reg in REGIONS:
        if reg == "A" and not a_cells:
            continue
        rows.append((reg, (lambda r, g=reg: r == g) if a.only else (lambda r, g=reg: r != g)))
    base = None
    for lab, keep in rows:
        model.noise_blocks = patched(keep, op_region, idle_region)
        try:
            c1, l2, l3, A1 = score(text, data, a.procs)
        finally:
            model.noise_blocks = _orig
        tot = l2 + l3
        base = tot if base is None else base
        name = lab if lab == "all" else ("only " if a.only else "no ") + lab
        print(f"{name:12s} c1 {c1:.1e}  2nd {l2:.4e}  3rd {l3:.4e}  total {tot:.4e}  "
              f"({100 * (tot - base) / base:+6.1f}%)  exp(-A1) {exact2.np.exp(-A1):.4f}", flush=True)


if __name__ == "__main__":
    main()
