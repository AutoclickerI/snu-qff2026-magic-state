"""Constrained mixed square/tree terminal contracts with ideal input resources.

The saved circuits have nonlocal encoders. Only the native terminal layers are
noisy in these counterfactuals. They are diagnostics, never complete candidates.
"""
import argparse
import collections
import json
import os
import sys
from pathlib import Path

for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/REBUILD20261027'))
from qtools.evaluator import frontend as f
from qtools.evaluator import sparse_walsh as sw
from qtools.validity import raw_check
from record_contract import complete
from joint import emit

D = [6, 20, 19, 10, 2, 22, 16]
A = [7, 21, 18, 4, 8, 23, 17]
B = [12, 26, 25, 11, 3, 28, 15]
C = [13, 27, 24, 5, 9, 29, 14]
ENC = [[(0, 2), (1, 5), (3, 6)], [(0, 4), (1, 6), (3, 5)],
       [(0, 6), (1, 2), (3, 4)]]
PIV = {0, 1, 3}


def ideal_contract_check(text, data):
    """Official exact-state check on native operations, without a grid claim.

    The complete QASM intentionally fails the official adjacency validator:
    the diagnostic uses ideal nonlocal encoders. This separate check verifies
    raw output state and deterministic records, using the unmodified exact
    simulator on the explicitly constructed native stream.
    """
    from tprep.exact import run, verify
    ops, dets = f.parse_current(text)
    native, _ = f.native_text(ops)
    bits = [o.bit for o in ops if o.bit is not None]
    pos = {b: i for i, b in enumerate(bits)}
    native += '\n' + '\n'.join('DETECTOR ' + ' '.join(f'rec[-{len(bits) - pos[b]}]' for b in sorted(row)) for row in dets)
    result = verify(native, data)
    state, inverse, _, _, wires = run(native, 36)
    values = []
    for pauli in 'XZ':
        for support in f.SUPPORTS:
            observable = state.stim.PauliString(state.n)
            for i in support:
                observable[wires[data[i]]] = pauli
            values.append(state.expectation(observable, inverse))
    result.pop('detector_values', None)
    result.update(six_stabilizers=values, ok=not result['errors'] and all(abs(v - 1) < 1e-9 for v in values),
                  scope='Official exact simulator on abstract native stream; excludes adjacency validation of ideal nonlocal encoders.')
    return result


def prep(ops, block, start, plus):
    for i, q in enumerate(block):
        isplus = (i not in PIV) if plus else (i in PIV)
        ops.append(f.Op('RX' if isplus else 'R', (q,), start))
    for k, layer in enumerate(ENC):
        for a, b in layer:
            ops.append(f.Op('CX', (block[b], block[a]) if plus else (block[a], block[b]), start + 1 + k))


def prep_shortened_c(ops, start):
    # span(012,034,135,6): the six-bit shortened Hamming code plus a
    # free last coordinate. Erasing coordinate 6 maps this into A's
    # X stabilizer space, so all three A-Z syndrome checks survive.
    for i, q in enumerate(C):
        ops.append(f.Op('RX' if i in (2,4,5,6) else 'R', (q,), start))
    for k, layer in enumerate([[(2,0),(4,3),(5,1)],[(2,1),(4,0),(5,3)]]):
        ops.extend(f.Op('CX', (C[a], C[b]), start + 1 + k) for a,b in layer)


def build(mask, cplus=True, compensated=False):
    ops = []
    # Perfect logical T input, using the documented Steane encoder.
    for i, q in enumerate(D):
        ops.append(f.Op('RX' if i in PIV | {2} else 'R', (q,), 0))
    ops += [f.Op('T', (D[2],), 1), f.Op('CX', (D[2], D[4]), 2),
            f.Op('CX', (D[2], D[5]), 3)]
    for k, layer in enumerate(ENC):
        ops.extend(f.Op('CX', (D[a], D[b]), 4 + k) for a, b in layer)
    if compensated:
        assert mask == 63 and cplus
        prep(ops, A, 2, True)
        prep(ops, B, 2, False)
        prep_shortened_c(ops, 2)
        ops.extend(f.Op('CX', (b,c), 6) for b,c in zip(B,C))
    else:
        prep(ops, A, 3, True)
        prep(ops, B, 3, False)
        prep(ops, C, 3, cplus)
    for i in range(7):
        ops += [f.Op('CX', (D[i], A[i]), 7), f.Op('CX', (B[i], C[i]), 7),
                f.Op('CX', (B[i], D[i]), 8)]
        if mask >> i & 1:
            ops.append(f.Op('CX', (C[i], A[i]), 8))
    for offset, block, kind in [(0, A, 'M'), (7, B, 'MX'), (14, C, 'MX' if cplus else 'M')]:
        ops.extend(f.Op(kind, (q,), 9, offset + i) for i, q in enumerate(block))
    f.DATA = D
    text = emit(ops, [])
    m = f.make_model(*f.parse_current(text))
    rec = complete(m, [])
    assert all(r['reference'] == 0 for r in rec['missing']), rec
    dets = [set(r['bits']) for r in rec['missing']]
    text = emit(ops, dets)
    raw = ideal_contract_check(text, D)
    folder = HERE / 'counterfactual'
    folder.mkdir(exist_ok=True)
    stem = folder / f'partial_square_{mask:02x}_c{"compensated" if compensated else "plus" if cplus else "zero"}'
    stem.with_suffix('.qasm').write_text(text)
    stem.with_suffix('.json').write_text(json.dumps(dict(data_qubits=D, roles=dict(D=D, A=A, B=B, C=C),
        square_mask=mask, compensated=compensated, ideal_contract=raw, gate_valid=False, record_contract=rec, noisy_source_ticks=[7, 8, 9],
        diagnostic_only=True, scope='Ideal nonlocal input/resource encoders; only terminal source channels noisy.'), indent=2) + '\n')
    return stem


def diagnose(stem, exact=False):
    m, eng, groups, nd, ks, psi, where, _ = sw.prepare(stem, True)
    removed = []
    for cid, ch in enumerate(m.chans):
        if m.labels[ch['ins']].time < 7:
            ch['p'] = 0
            for ff in groups[cid]:
                ff['p'] = 0
            removed.append(cid)
    active = sum(1 << i for i, p in enumerate(eng.projs) if p[:2] != (0, 0))
    cache = {}
    def numerator(s, d, e):
        if (s, d) not in cache:
            cache[s, d] = eng.ntable(s, d)
        _, n = cache[s, d]
        return 0. if n is None else max(0., float(n[e]))
    faults = [ff for ff in m.faults if ff['p']]
    first = sum(ff['p'] / .001 * numerator(ff['s'], ff['d'], ff['e']) for ff in faults)
    bins = collections.defaultdict(list)
    for ff in faults:
        bins[ff['d'] & ~active].append(ff)
    second = 0.
    for fs in bins.values():
        for i, a in enumerate(fs):
            for b in fs[i + 1:]:
                if a['chan'] != b['chan']:
                    second += a['p'] * b['p'] / 1e-6 * numerator(a['s'] ^ b['s'], a['d'] ^ b['d'], a['e'] ^ b['e'])
    out = dict(stem=str(stem.relative_to(ROOT)), c1=first, pair_numerator=second,
               c2_loss_valid=first < 1e-10, removed_channels=len(removed), scope='Only source ticks 7,8,9 noisy; earlier encoders and their attached idles ideal.')
    if exact:
        compiled, elim = sw.compile_best(m, eng, groups, nd, ks, save=False)
        sw._CTX.update(eng=eng, ks=ks, psi=psi, where=where, compiled=compiled, elim=elim)
        try:
            vals = [sw._row(k) for k in [None] + eng.keys]
            acc = vals[0]['value']
            obs = sum(w * b * v['value'] for w, b, v in zip(eng.W, eng.beta, vals[1:]))
            out.update(loss=(acc - obs) / (2 * acc), acceptance=acc)
        finally:
            sw._CTX.clear()
            sw.COLUMNS.clear()
    stem.with_suffix('.diagnostic.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps(out), flush=True)
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--masks', default='127,63,31,0')
    ap.add_argument('--exact', action='store_true')
    args = ap.parse_args()
    for mask in map(int, args.masks.split(',')):
        diagnose(build(mask), args.exact)
