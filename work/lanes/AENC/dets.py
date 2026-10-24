"""Deterministic record parities of a circuit (frontend Pauli model) and a detector basis for edited circuits.

A record parity S is deterministic iff its pulled-back Pauli has no X part on the initial |0> wires and commutes
with every T rotation. complete(stem, keep_rows) keeps the given rows that are still deterministic and extends them
with sparse generators of the full deterministic group; reference values are reported (sparse_walsh needs 0).
"""
import sys, json, re
from pathlib import Path
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/MAIN/sparse')
import frontend as fa


def model(stem):
    stem = Path(stem)
    text = stem.with_suffix('.qasm').read_text()
    fa.DATA = json.loads(stem.with_suffix('.json').read_text())['data_qubits']
    ops, dets = fa.parse_current(text)
    m = fa.make_model(ops, dets)
    return m, ops, dets


def group(m):
    """Basis of the deterministic record-parity group as sets of record bits (GF(2) kernel)."""
    bits = sorted(m.record_ps)
    rx = [r[0] for r in m.rots]
    vecs = []
    for b in bits:
        x, z, _ = m.record_ps[b]
        c = 0
        for j, xr in enumerate(rx):
            c |= ((z & xr).bit_count() & 1) << j
        vecs.append((x, c))
    # Gaussian elimination on the map b -> (x, c); track combinations
    piv = {}
    kernel = []
    for i, (x, c) in enumerate(vecs):
        key = (c << 4096) | x
        comb = 1 << i
        while key:
            h = key.bit_length() - 1
            if h not in piv:
                piv[h] = (key, comb)
                break
            k2, c2 = piv[h]
            key ^= k2; comb ^= c2
        if not key:
            kernel.append(comb)
    return [sorted(bits[j] for j in range(len(bits)) if comb >> j & 1) for comb in kernel], bits


def reduce_rows(rows, bits):
    idx = {b: i for i, b in enumerate(bits)}
    return [sum(1 << idx[b] for b in r) for r in rows]


def rank(vs):
    piv = {}
    r = 0
    for v in vs:
        while v:
            h = v.bit_length() - 1
            if h not in piv:
                piv[h] = v; r += 1; break
            v ^= piv[h]
    return r


def pauli_rows(stem):
    """Rows of a stem that lie in its Pauli kernel (the others are magic-structure rows)."""
    m, ops, dets = model(stem)
    G, bits = group(m)
    Gv = reduce_rows(G, bits); g = rank(Gv)
    idx = {b: i for i, b in enumerate(bits)}
    return [sorted(d) for d in dets if rank(Gv + [sum(1 << idx[b] for b in d)]) == g]


def complete(stem, keep_rows, base=None):
    m, ops, dets = model(stem)
    G, bits = group(m)
    idx = {b: i for i, b in enumerate(bits)}
    Gv = reduce_rows(G, bits)
    gr = rank(Gv)
    prow = {tuple(r) for r in pauli_rows(base)} if base else set()
    rows = []
    cur = []
    for r in keep_rows:                            # original rows on surviving records: Pauli rows only if still in
        if any(b not in idx for b in r): continue  # the kernel; magic rows (T checks) kept, Engine re-checks all
        v = sum(1 << idx[b] for b in r)
        if base and tuple(sorted(r)) in prow and rank(Gv + [v]) != gr: continue
        if rank(cur + [v]) == len(cur) + 1:
            cur.append(v); rows.append(sorted(r))
    gr = rank(Gv + cur)
    # extend with sparse group elements: try weight-ordered reduced kernel vectors
    cand = sorted(G, key=len)
    for r in cand:
        v = sum(1 << idx[b] for b in r)
        if rank(cur + [v]) == len(cur) + 1:
            cur.append(v); rows.append(sorted(r))
    assert len(rows) == gr, (len(rows), gr)
    return rows, gr


if __name__ == '__main__':
    m, ops, dets = model(sys.argv[1])
    G, bits = group(m)
    rows = reduce_rows([sorted(d) for d in dets], bits)
    Gv = reduce_rows(G, bits)
    print('records', len(bits), 'group dim', rank(Gv), 'rows', len(dets), 'row rank', rank(rows), 'rows in group', rank(Gv + rows) == rank(Gv))
