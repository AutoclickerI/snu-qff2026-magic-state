"""Independent finite-state and schedule-count checks for the L5 exact search.

Uses Python column-by-column elimination and NumPy layer-walk DP, independently
of the C++ canonical-word enumerator. All output remains in EXENC.
"""
import sys
sys.dont_write_bytecode = True
import itertools
import json
import time
from collections import Counter
from pathlib import Path
import numpy as np
import exenc


def rref(rows, n):
    rows = list(rows)
    rank = 0
    for bit in range(n):
        found = next((j for j in range(rank, len(rows)) if rows[j] & (1 << bit)), None)
        if found is None:
            continue
        rows[rank], rows[found] = rows[found], rows[rank]
        for j in range(len(rows)):
            if j != rank and rows[j] & (1 << bit):
                rows[j] ^= rows[rank]
        rank += 1
    return tuple(rows)


def independent_graph(cells):
    avail = sorted(cells)
    edges = [(avail.index(u), avail.index(v)) for u in avail
             for v in avail if v in exenc.synth.nbrs(u)]
    target = rref([sum(1 << avail.index(cells[j]) for j in row)
                   for row in exenc.rows_for("plus")], len(cells))
    states, ids, distance, transitions = [target], {target: 0}, [0], []
    for s in states:
        row = []
        for u, v in edges:
            nxt = rref([x ^ (1 << v) if x & (1 << u) else x for x in s], len(cells))
            if nxt not in ids:
                ids[nxt] = len(states)
                states.append(nxt)
                distance.append(distance[ids[s]] + 1)
            row.append(ids[nxt])
        transitions.append(row)
    initials = [ids[rref([1 << j for j in piv], len(cells))]
                for piv in itertools.combinations(range(len(cells)), 4)]
    return states, initials, distance, np.array(transitions, dtype=np.int32), edges


def main():
    started = time.monotonic()
    result = json.loads((exenc.HERE / "prepA_L5_exact_stats.json").read_text())
    cells = result["cells"]
    states, initials, distance, trans, edges = independent_graph(cells)
    assert len(states) == result["states"] == 11811
    assert min(distance[i] for i in initials) == result["min_cx"] == 11
    assert [Counter(distance)[d] for d in range(max(distance) + 1)] == result["distance_histogram"]
    # Every transition is an involution; independently confirm the state space is
    # all rank-four subspaces using the Gaussian binomial coefficient.
    gaussian = 1
    numerator = denominator = 1
    for i in range(4):
        numerator *= 2 ** (7-i) - 1
        denominator *= 2 ** (4-i) - 1
    gaussian = numerator // denominator
    assert gaussian == len(states)
    indices = np.arange(len(states))
    for e in range(len(edges)):
        assert np.array_equal(trans[trans[:, e], e], indices)
    layers = []
    for bits in range(1, 1 << len(edges)):
        chosen = [j for j in range(len(edges)) if bits & (1 << j)]
        qubits = [q for j in chosen for q in edges[j]]
        if len(set(qubits)) == len(qubits):
            step = indices
            for j in chosen:
                step = trans[step, j]
            layers.append((len(chosen), step))
    assert len(layers) == result["legal_layers"] == 94
    bound = result["alternative_depth_bound"]
    max_cx = max(x["cx"] for x in result["counted_classes"])
    # count[d,c,s]: number of ordered nonempty matching-layer sequences from
    # target to state s with exactly d layers and c CX. Reversal is a bijection
    # to preparation circuits. No trace canonicalization is used in this DP.
    previous = np.zeros((max_cx + 1, len(states)), dtype=np.int64)
    previous[0, 0] = 1
    checked = []
    min_depth = None
    for depth in range(1, bound + 1):
        current = np.zeros_like(previous)
        for size, step in layers:
            current[size:] += previous[:-size, step]
        assert current.min() >= 0  # Counts here remain far below int64 overflow.
        for cx in range(max_cx + 1):
            count = int(current[cx, initials].sum())
            if count and min_depth is None:
                min_depth = depth
            expected = sum(c["count"] for c in result["classes"]
                           if c["cx"] == cx and c["depth"] == depth)
            assert count == expected, (cx, depth, count, expected)
            if count:
                checked.append({"cx": cx, "depth": depth, "count": count})
        previous = current
    assert min_depth == result["min_depth"] == 5
    # Exhaustive Pauli signature classification (128 Z masks x 128 X masks).
    labels = range(1, 8)
    for zbits in range(128):
        zset = {cells[j] for j in range(7) if zbits & (1 << j)}
        tag = 0
        for j in range(7):
            if zbits & (1 << j):
                tag ^= (j + 1) | 8
        assert (bool(tag & 8) != bool(tag & 7)) == bool(exenc.synth.z_class(zset, cells))
        for xbits in range(128):
            xset = {cells[j] for j in range(7) if xbits & (1 << j)}
            xsyn = 0
            for j in range(7):
                if xbits & (1 << j):
                    xsyn ^= j + 1
            assert xsyn == exenc.synth.x_syndrome(xset, cells)
    record = {"independent_states": len(states), "gaussian_binomial": gaussian,
              "min_cx": 11, "min_depth": min_depth,
              "all_layer_schedule_counts_agree": checked,
              "pauli_signature_pairs_checked": 16384,
              "runtime_seconds": time.monotonic() - started}
    (exenc.HERE / "verification.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record), flush=True)


if __name__ == "__main__":
    main()
