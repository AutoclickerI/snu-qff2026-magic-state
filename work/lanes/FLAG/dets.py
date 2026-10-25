"""Deterministic record parities of a QASM candidate (Clifford proxy: T -> S, T_DAG -> S_DAG).

The round's detectors are Pauli parities of a code state; replacing T by S keeps every such parity's
determinism (the data stay in the code space), so this proxy derives round detectors. The judge's exact
check (fast_check) is the final word.

usage: dets.py <stem> [records...]      check the stem's detectors; with records, print a basis of the
                                        deterministic parities supported on those records (c indices)
API: records_matrix(stem) -> (meas_c_index list, samples), check(stem), basis(stem, recs)
"""
import sys, re
import numpy as np
sys.path.insert(0, "/home/jihoon/competitions/quantumn/upstream/snu-qff2026-problem")
from tprep.qasm import convert
import stim

CRE = re.compile(r"c\[(\d+)\]")


def stim_clifford(text):
    st, labels, errors = convert(text)
    assert not errors, errors
    out = []
    for ln in st.splitlines():
        s = ln.strip()
        if s.startswith("T_DAG "):
            ln = "S_DAG " + s[6:]
        elif s.startswith("T "):
            ln = "S " + s[2:]
        out.append(ln)
    return "\n".join(out)


def meas_order(text):
    """c index of each measurement in program order (QASM measure statements)."""
    order = []
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("measure"):
            order.append(int(CRE.findall(s)[0]))
    return order


def detectors(text):
    return [sorted(map(int, CRE.findall(ln))) for ln in text.splitlines() if ln.strip().startswith("// DETECTOR")]


def samples(text, shots=1024, seed=0):
    circ = stim.Circuit(stim_clifford(text))
    circ = stim.Circuit("\n".join(l for l in str(circ).splitlines() if not l.startswith("DETECTOR")
                                  and not l.startswith("OBSERVABLE")))
    smp = circ.compile_sampler(seed=seed).sample(shots).astype(np.uint8)
    order = meas_order(text)
    assert smp.shape[1] == len(order), (smp.shape, len(order))
    col = {c: k for k, c in enumerate(order)}
    return smp, col


def check(text, shots=1024):
    smp, col = samples(text, shots)
    bad = []
    for d in detectors(text):
        v = np.bitwise_xor.reduce(smp[:, [col[c] for c in d]], axis=1)
        if v.min() != v.max():
            bad.append(d)
    return bad


def nullspace_gf2(M):
    """Basis of {x : M x = 0} over GF(2); M is (rows, n) uint8."""
    M = M.copy() % 2
    rows, n = M.shape
    piv = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, rows) if M[i, c]), None)
        if p is None:
            continue
        M[[r, p]] = M[[p, r]]
        for i in range(rows):
            if i != r and M[i, c]:
                M[i] ^= M[r]
        piv.append(c)
        r += 1
        if r == rows:
            break
    free = [c for c in range(n) if c not in piv]
    basis = []
    for f in free:
        x = np.zeros(n, np.uint8)
        x[f] = 1
        for i, c in enumerate(piv):
            if M[i, f]:
                x[c] = 1
        basis.append(x)
    return basis


def basis(text, recs, shots=1024):
    smp, col = samples(text, shots)
    sub = smp[:, [col[c] for c in recs]]
    M = sub ^ sub[0]
    return [[recs[i] for i in np.nonzero(b)[0]] for b in nullspace_gf2(M)]


def in_span(text, recs, parity, shots=1024):
    smp, col = samples(text, shots)
    v = np.bitwise_xor.reduce(smp[:, [col[c] for c in parity]], axis=1)
    return v.min() == v.max()


if __name__ == "__main__":
    text = open(sys.argv[1] + ".qasm").read()
    if len(sys.argv) == 2:
        bad = check(text)
        print(f"{len(detectors(text))} detectors, {len(bad)} non-deterministic under the proxy: {bad}")
    else:
        recs = [int(x) for x in sys.argv[2:]]
        for b in basis(text, recs):
            print(" ".join(f"c[{c}]" for c in b))
