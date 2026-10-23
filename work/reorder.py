"""Physically identical re-draws of a circuit's official MC sample.

Permutes the written order of instructions between consecutive barrier/comment lines as a random
linear extension of the per-qubit order, keeping measurements in their written order. The judge's
schedule (tprep.noise.schedule) is unchanged, so every noise channel is the same and only the order
in which xtim draws them changes: the true 1-F is identical and the seed-0 score is a fresh draw.
Each variant is verified (same instruction multiset, same time steps, same idle gaps) before scoring.

    python reorder.py <stem> <n variants> [procs] [first variant]   ->  reorder/<name>_r<k>.qasm/.json
"""
import json
import os
import random
import sys

import tprep.noise as tn
import tprep.qasm as tq
from fast_check import check


def segments(lines):
    """Indices of movable instruction lines, grouped between fixed lines (header, barrier, comment)."""
    segs, cur = [], []
    for i, line in enumerate(lines):
        s = line.strip()
        op = s.split()[0] if s else ""
        if op in ("h", "t", "tdg", "s", "sdg", "x", "y", "z", "id", "cx", "reset", "measure"):
            cur.append(i)
        else:
            if cur:
                segs.append(cur)
            cur = []
    if cur:
        segs.append(cur)
    return segs


def qubits(line):
    return [int(t.split("]")[0]) for t in line.split("q[")[1:]]


def shuffle(lines, rng):
    out = list(lines)
    for seg in segments(lines):
        preds = {i: set() for i in seg}
        last, last_meas = {}, None
        for i in seg:
            for q in qubits(lines[i].split("->")[0]):
                if q in last:
                    preds[i].add(last[q])
                last[q] = i
            if lines[i].lstrip().startswith("measure"):
                if last_meas is not None:
                    preds[i].add(last_meas)
                last_meas = i
        done, order = set(), []
        while len(order) < len(seg):
            i = rng.choice([j for j in seg if j not in done and preds[j] <= done])
            done.add(i)
            order.append(i)
        for slot, i in zip(seg, order):
            out[slot] = lines[i]
    return out


def signature(text):
    """Multiset of (instruction, time steps) plus idle gaps keyed by instruction: the noise model."""
    stim, errors = tq.to_stim(text)
    assert not errors, errors
    prog, steps, gaps = tn.schedule(stim)
    key = [(ins.name, tuple(ins.qubits), tuple((tuple(g), t) for g, t in st)) for ins, st in zip(prog, steps)]
    return sorted(key), sorted((key[i], q, t0, n) for i, q, t0, n in gaps)


def main():
    stem, n = sys.argv[1], int(sys.argv[2])
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    k0 = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    text = open(stem + ".qasm").read()
    meta = json.load(open(stem + ".json"))
    lines = text.split("\n")
    ref = signature(text)
    name = os.path.basename(stem)
    os.makedirs("reorder", exist_ok=True)
    for k in range(k0, k0 + n):
        var = "\n".join(shuffle(lines, random.Random(k)))
        assert signature(var) == ref, f"variant {k} changes the schedule"
        rep = check(var, meta["data_qubits"], shots=10**8, seed=0, procs=procs)
        out = f"reorder/{name}_r{k}"
        open(out + ".qasm", "w").write(var)
        json.dump({"data_qubits": meta["data_qubits"], "score": rep.score, "acceptance": rep.acceptance,
                   "n_2q": rep.n_2q, "passed": rep.passed, "source": f"{stem} reordered, rng {k}"},
                  open(out + ".json", "w"), indent=1)
        print(f"{name}_r{k} 1-F {rep.score:.5e} acc {rep.acceptance:.4f} 2q {rep.n_2q} pass {rep.passed}", flush=True)


if __name__ == "__main__":
    main()
