#!/usr/bin/env python
"""Exact 1-F with several regions of ablate.py noiseless at once.

    ablate_multi.py <qasm> --pre-end S --round-start R --a cells [--procs N] wait,prep wait,A ...
Each positional argument is a comma-separated set of regions (pre, wait, moves, A, prep, round) made noiseless.
"""
import argparse
import json
import ablate
import model
import exact2


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("qasm")
    ap.add_argument("--pre-end", type=int, required=True)
    ap.add_argument("--round-start", type=int, required=True)
    ap.add_argument("--a", default="")
    ap.add_argument("--procs", type=int, default=24)
    ap.add_argument("sets", nargs="+")
    a = ap.parse_args()
    text = open(a.qasm).read()
    data = json.load(open(a.qasm.rsplit(".", 1)[0] + ".json"))["data_qubits"]
    a_cells = {int(x) for x in a.a.split(",") if x}
    op_region, idle_region = ablate.labeller(set(data), a_cells, a.pre_end, a.round_start)
    for s in a.sets:
        off = set(s.split(","))
        model.noise_blocks = ablate.patched(lambda r: r not in off, op_region, idle_region)
        try:
            c1, l2, l3, A1 = ablate.score(text, data, a.procs)
        finally:
            model.noise_blocks = ablate._orig
        print(f"no {s:22s} 2nd {l2:.4e}  3rd {l3:.4e}  total {l2 + l3:.4e}  exp(-A1) {exact2.np.exp(-A1):.4f}", flush=True)


if __name__ == "__main__":
    main()
