"""Stabilizer analysis of the B/C resource of a v36h-family circuit (stim, T/TDG dropped: B/C is a product with data).

simulate(ops, upto): runs every native op with time <= upto (inits, measurements, CX, H) on a stim TableauSimulator.
cstate(sim): the CSS structure of C after B->C: X-stabilizer space and Z-stabilizer space over C (code-order masks),
and whether B is |0_L>.  Used to find zero-gate |R_V> preparations (init flips) and to verify built candidates.
"""
import sys, itertools
from pathlib import Path
import stim
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/PCC/ev')
from frontend import parse_current

B = [6, 26, 13, 11, 4, 23, 27]
C = [12, 25, 19, 17, 5, 29, 28]
GEN = [0b1010101, 0b1100110, 0b1111000]          # C2 generators {0,2,4,6},{1,2,5,6},{3,4,5,6} (bit i = code index i)
C2 = sorted({a ^ b ^ c for a in (0, GEN[0]) for b in (0, GEN[1]) for c in (0, GEN[2])})
HAM = C2 + [w ^ 0x7f for w in C2]                  # Hamming [7,4] (C2 plus complements) = C2-perp


def load(stem):
    ops, dets = parse_current(Path(stem).with_suffix('.qasm').read_text())
    return ops, dets


def simulate(ops, upto, nq=40, seed=0):
    sim = stim.TableauSimulator(seed=seed)
    sim.set_num_qubits(nq)
    for op in ops:
        if op.time > upto:
            continue
        k, qs = op.kind, op.qs
        if k == 'R':
            sim.reset_z(*qs)
        elif k == 'RX':
            sim.reset_x(*qs)
        elif k == 'M':
            sim.measure(qs[0])
        elif k == 'MX':
            sim.measure_many  # noqa
            sim.h(qs[0]); sim.measure(qs[0]); sim.h(qs[0])
        elif k == 'CX':
            sim.cnot(*qs)
        elif k == 'H':
            sim.h(*qs)
        elif k in ('TDG', 'T', 'T_DAG', 'I'):
            pass
        else:
            raise ValueError(k)
    return sim


def pauli(nq, xs=(), zs=()):
    xv = [False] * nq
    zv = [False] * nq
    for q in xs:
        xv[q] ^= True
    for q in zs:
        zv[q] ^= True
    return stim.PauliString.from_numpy(xs=__import__('numpy').array(xv), zs=__import__('numpy').array(zv))


def det(sim, p):
    return sim.peek_observable_expectation(p)


def css_space(sim, cells, kind, nq=40):
    """all masks m (bit i = cells[i]) with deterministic X(m) (kind 'X') or Z(m) expectation"""
    out = []
    for m in range(1, 1 << len(cells)):
        qs = [cells[i] for i in range(len(cells)) if m >> i & 1]
        p = pauli(nq, xs=qs) if kind == 'X' else pauli(nq, zs=qs)
        if det(sim, p) != 0:
            out.append(m)
    return out


def rank(vecs):
    piv = {}
    for v in vecs:
        while v:
            h = v.bit_length() - 1
            if h not in piv:
                piv[h] = v
                break
            v ^= piv[h]
    return len(piv)


def b_is_zeroL(sim, nq=40):
    ok = all(det(sim, pauli(nq, xs=[B[i] for i in range(7) if g >> i & 1])) != 0 for g in GEN)
    ok &= all(det(sim, pauli(nq, zs=[B[i] for i in range(7) if h >> i & 1])) != 0 for h in HAM if h)
    return ok


def cstate(sim, nq=40):
    xs = css_space(sim, C, 'X', nq)
    zs = css_space(sim, C, 'Z', nq)
    return dict(X=xs, Z=zs, rX=rank(xs), rZ=rank(zs), B0L=b_is_zeroL(sim, nq))


def fmt(m):
    return '{' + ','.join(str(i) for i in range(7) if m >> i & 1) + '}'


if __name__ == '__main__':
    stem = sys.argv[1]
    ops, dets = load(stem)
    sim = simulate(ops, 44)
    print('reference after tick 44:', {k: (v if isinstance(v, (bool, int)) else [fmt(m) for m in v][:8]) for k, v in cstate(sim).items()})
