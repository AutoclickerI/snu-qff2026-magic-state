"""1-F and acceptance with judge noise kept only in one region of a steane_full circuit
(regions from its '// region <name>' markers; lines before the first marker are 'pre').

    python regions.py <stem> [shots] [procs]
"""
import json
import re
import sys

sys.path.insert(0, "/home/jihoon/competitions/quantumn/work")
import region_decomp as rd  # noqa: E402
import tprep.qasm as tq  # noqa: E402


def labels(text):
    reg, cur, k = {}, "pre", 0
    k_reg = {}
    for no, line in enumerate(text.splitlines(), start=1):
        if line.startswith("// region "):
            cur = line.split()[2]
        s = line.split("//")[0].strip()
        if not s or s.startswith(("OPENQASM", "include", "qreg", "creg")):
            continue
        k += 1
        k_reg[k] = cur
    stim, labs, errors = tq.convert(text)
    out = {}
    for j, lab in enumerate(labs):
        m = re.match(r"instruction (\d+) ", lab)
        if m:
            out[j] = k_reg[int(m.group(1))]
    return out


if __name__ == "__main__":
    stem = sys.argv[1]
    shots = int(float(sys.argv[2])) if len(sys.argv) > 2 else 10**7
    procs = int(sys.argv[3]) if len(sys.argv) > 3 else 40
    text = open(stem + ".qasm").read()
    data = json.load(open(stem + ".json"))["data_qubits"]
    reg = labels(text)
    names = sorted(set(reg.values()), key=list(dict.fromkeys(reg.values())).index)
    for name in ["all"] + names:
        keep = (lambda r: True) if name == "all" else (lambda r, n=name: r == n)
        rep = rd.run(text, data, reg, keep, lambda r, q, t, keep=keep: keep(r), procs, shots)
        print(f"{name:8s} 1-F {rep.score:.4e} ± {rep.sem:.1e} acc {rep.acceptance:.4f}", flush=True)
