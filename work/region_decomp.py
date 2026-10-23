"""1-F of one circuit with judge noise kept only in chosen regions (official engine, 1e8 shots, seed 0).

Region of an instruction: 'pre' if its QASM statement comes before line <cut> (the first final-round
line), else 'cyc'. Gate, preparation and measurement noise is kept per instruction; an idle gap
belongs to the instruction that starts it, and 'tail' gaps are data idles that run to the end.

    python region_decomp.py <stem> <cut line> [procs] [shots]
"""
import dataclasses
import json
import re
import sys

import tprep.noise as tn
import tprep.qasm as tq
import fast_check

_orig = tn.noise_blocks


def regions(text, cut):
    """stim line index -> 'pre' | 'cyc', from the judge's own labels."""
    k, k_of_line = 0, {}
    for no, line in enumerate(text.splitlines(), start=1):
        s = line.split("//")[0].strip()
        if not s or s.startswith(("OPENQASM", "include", "qreg", "creg")):
            continue
        k += 1
        k_of_line[no] = k
    k_cut = min(v for no, v in k_of_line.items() if no >= cut)
    stim, labels, errors = tq.convert(text)
    assert not errors, errors
    reg = {}
    for j, lab in enumerate(labels):
        m = re.match(r"instruction (\d+) ", lab)
        if m:
            reg[j] = "pre" if int(m.group(1)) < k_cut else "cyc"
    return stim, reg


def run(text, data, reg, keep_gate, keep_idle, procs, shots):
    """keep_gate(region) -> bool; keep_idle(region, qubit, is_tail) -> bool."""
    def patched(t, p, noise=tn.STANDARD, first_order=False):
        prog, steps, gaps = tn.schedule(t)
        end = max(s for g in steps for _, s in g) + 1
        prog, blocks = _orig(t, p, dataclasses.replace(noise, idle=0.0), first_order)
        out = [block if keep_gate(reg.get(ins.line_no - 1, "cyc")) else [ins.text]
               for ins, block in zip(prog, blocks)]
        for i, q, first, n in gaps:
            if keep_idle(reg.get(prog[i].line_no - 1, "cyc"), q, first + n == end):
                out[i].append(f"DEPOLARIZE1({tn._repeated(p * noise.idle, n, first_order)}) {q}")
        return prog, out

    tn.noise_blocks = patched
    try:
        return fast_check.check(text, data, shots=shots, procs=procs)
    finally:
        tn.noise_blocks = _orig


if __name__ == "__main__":
    stem, cut = sys.argv[1], int(sys.argv[2])
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    shots = int(float(sys.argv[4])) if len(sys.argv) > 4 else 10**8
    text = open(stem + ".qasm").read()
    data = json.load(open(stem + ".json"))["data_qubits"]
    stim, reg = regions(text, cut)
    D = set(data)
    cases = [
        ("all", lambda r: True, lambda r, q, t: True),
        ("no idle", lambda r: True, lambda r, q, t: False),
        ("pre only", lambda r: r == "pre", lambda r, q, t: r == "pre"),
        ("cycle only", lambda r: r == "cyc", lambda r, q, t: r == "cyc"),
        ("cycle gates only", lambda r: r == "cyc", lambda r, q, t: False),
        ("cycle data tails only", lambda r: False, lambda r, q, t: r == "cyc" and q in D and t),
        ("cycle gates + data tails", lambda r: r == "cyc", lambda r, q, t: r == "cyc" and q in D and t),
    ]
    for lab, g, i in cases:
        rep = run(text, data, reg, g, i, procs, shots)
        print(f"{lab:26s} 1-F {rep.score:.4e} ± {rep.sem:.1e} acc {rep.acceptance:.4f}", flush=True)
