"""Native state synthesis with a measurement-aware boundary.

This bounded beam search compares two interfaces on the same physical graph:
all helpers cleared, or helpers carrying only the logical computational bit.
The latter may be measured in X with one affine logical-Z frame. No SWAP
routing, fixed encoder circuit, or CP-SAT model is used. Neither a gate-count
win nor a raw-valid input module is a fault-tolerant/full-circuit score.
"""
import argparse
import hashlib
import heapq
import json
import os
from pathlib import Path
import random
import sys
import time

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[key] = "1"

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "work/lanes/FRAME20261027"))
sys.path.insert(0, str(ROOT / "work/lanes/END2_20261027"))
import frame_tools as ft
from joint import emit

A = [7, 14, 13, 9, 8, 21, 15]
D = [6, 20, 19, 10, 2, 22, 16]
CELLS = A + D
GEN = [85, 102, 120, 7]
EDGES = [(i, j) for i, a in enumerate(CELLS)
         for j, b in enumerate(CELLS)
         if abs(a // 6 - b // 6) + abs(a % 6 - b % 6) == 1]
TARGET_D = [sum(((g >> i) & 1) << j for j, g in enumerate(GEN))
            for i in range(7)]


def pack(rows):
    return sum(v << (4 * i) for i, v in enumerate(rows))


def unpack(state):
    return [(state >> (4 * i)) & 15 for i in range(len(CELLS))]


def is_product(state):
    rows = unpack(state)
    return sum(bool(x) for x in rows) == 4 and rows.count(8) == 1


def rank(rows):
    piv = {}
    for value in rows:
        while value:
            bit = value.bit_length() - 1
            if bit not in piv:
                piv[bit] = value
                break
            value ^= piv[bit]
    return len(piv)


def make_witness(initial, path, helper_mask, mode, seed, elapsed):
    """Replay native CNOTs, then verify using unmodified official exact code."""
    rows = unpack(initial)
    assert rank(rows) == 4 and rows.count(8) == 1
    source = rows.copy()
    gates = list(reversed(path))
    last = [-1] * len(CELLS)
    layers = []
    for a, b in gates:
        tick = max(last[a], last[b]) + 1
        while len(layers) <= tick:
            layers.append([])
        layers[tick].append([CELLS[a], CELLS[b]])
        last[a] = last[b] = tick
        rows[b] ^= rows[a]
    target = [8 if helper_mask >> i & 1 else 0 for i in range(7)] + TARGET_D
    assert rows == target
    magic = CELLS[source.index(8)]
    operations = [ft.f.Op("CX", tuple(edge), tick + 2)
                  for tick, layer in enumerate(layers) for edge in layer]
    operations.append(ft.f.Op("T", (magic,), 1))
    for i, q in enumerate(CELLS):
        first = min((o.time for o in operations if q in o.qs), default=2)
        operations.append(ft.f.Op("RX" if source[i] else "R", (q,), first - 1))
    measured = [A[i] for i in range(7) if helper_mask >> i & 1]
    first_measure = max(o.time for o in operations) + 1
    frame_bits = set()
    for index, q in enumerate(measured):
        bit = 400 + index
        operations.append(ft.f.Op("MX", (q,), first_measure, bit))
        frame_bits.add(bit)
    text = emit(sorted(operations, key=lambda o: (o.time, o.kind, o.qs)), [])
    if measured:
        text += "// FRAME_X(0)\n// FRAME_Z(0) " + " ".join(
            f"c[{b}]" for b in sorted(frame_bits)) + "\n"
    raw = ft.raw_check(text, D)
    assert raw["ok"], raw
    out = dict(mode=mode, seed=seed, helper_mask=helper_mask,
               cells=CELLS, data_qubits=D, initial_rows=dict(zip(CELLS, source)),
               magic_input=magic, layers=layers, cx=len(gates),
               cx_layers=len(layers), ticks=max(o.time for o in operations) + 1,
               helper_measurements=measured, frame_Z_bits=sorted(frame_bits),
               raw=raw, seconds=elapsed, adjacent=True,
               scope="Raw-valid native input module only; no complete fault-tolerant performance claim.",
               qasm_sha256=hashlib.sha256(text.encode()).hexdigest())
    folder = HERE / "candidates"
    folder.mkdir(exist_ok=True)
    name = f"input_{mode}_seed{seed}_cx{len(gates)}"
    stem = folder / name
    stem.with_suffix(".qasm").write_text(text)
    stem.with_suffix(".json").write_text(json.dumps(out, indent=2) + "\n")
    out["stem"] = str(stem.relative_to(ROOT))
    return out


def search(mode="clear", seed=0, beam=1800, depth=28, seconds=90):
    start = time.perf_counter()
    rng = random.Random(seed)
    masks = range(128) if mode == "logical_frame" else [0]
    front = [(pack([8 if mask >> i & 1 else 0 for i in range(7)] + TARGET_D),
              (), mask) for mask in masks]
    seen = {state for state, _, _ in front}
    # The native graph, not an abstract gate list, defines every available move.
    # We diversify the heuristic; correctness is exact algebra + official check.
    basis_cost = [0] + [v.bit_count() * (0.8 + rng.random() * 0.4)
                       for v in range(1, 16)]
    records = []
    for step in range(1, depth + 1):
        candidates = {}
        for state, path, mask in front:
            rows = unpack(state)
            for a, b in EDGES:
                value = rows[a]
                if not value:
                    continue
                after = state ^ (value << (4 * b))
                if after in seen or after in candidates:
                    continue
                new_path = path + ((a, b),)
                if is_product(after):
                    witness = make_witness(after, new_path, mask, mode, seed,
                                           time.perf_counter() - start)
                    return dict(completed=True, outcome="witness", witness=witness,
                                explored=len(seen), steps=step, trace=records)
                nr = rows.copy()
                nr[b] ^= value
                nonzero = sum(bool(x) for x in nr)
                equal = sum(nr[x] != 0 and nr[x] == nr[y] for x, y in EDGES) / 2
                score = nonzero * 7.0 + sum(basis_cost[x] for x in nr) * 0.22 - equal * 1.1
                score += 0.7 * (8 not in nr) + rng.random() * 3.0
                candidates[after] = (score, new_path, mask)
        if not candidates:
            return dict(completed=True, outcome="frontier_exhausted", explored=len(seen), trace=records)
        best = heapq.nsmallest(beam, candidates.items(), key=lambda row: row[1][0])
        front = [(state, value[1], value[2]) for state, value in best]
        seen.update(candidates)
        record = dict(step=step, best_nonzero=min(sum(bool(v) for v in unpack(row[0])) for row in front),
                      states=len(seen), seconds=time.perf_counter() - start)
        records.append(record)
        if step % 4 == 0:
            print(json.dumps(dict(mode=mode, seed=seed, **record)), flush=True)
        if len(seen) > 1000000:
            seen = {state for state, _, _ in front}
        if time.perf_counter() - start >= seconds:
            break
    return dict(completed=True, outcome="budget_exhausted", explored=len(seen), trace=records,
                seconds=time.perf_counter() - start)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["clear", "logical_frame"], default="clear")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--beam", type=int, default=1800)
    ap.add_argument("--depth", type=int, default=28)
    ap.add_argument("--seconds", type=float, default=90)
    args = ap.parse_args()
    result = search(**vars(args))
    result.update(parameters=vars(args), source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (HERE / f"beam_{args.mode}_{args.seed}.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
