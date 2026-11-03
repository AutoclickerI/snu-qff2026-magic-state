"""Assemble native measured-helper A and BC factories with the source.

The full source and every physical preparation operation are retained.  The
exact rotation-state record quotient derives the terminal checks, including
the random helper outcomes and any reused conditional source states.  No
perfect resource, reset, removed idle, or unrecorded Pauli correction is used.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import copy
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/END2_20261027'))
sys.path.insert(0, str(ROOT / 'work/lanes/REBUILD20261027'))
from qtools import price, write_stem
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from joint import emit
from partial_contract import make_four_square_contract
from record_contract import complete, singles


def null_rows(vectors, width):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    for bit in sorted(pivots):
        for other in pivots:
            if other != bit and pivots[other] >> bit & 1:
                pivots[other] ^= pivots[bit]
    rows = []
    for bit in range(width):
        if bit in pivots:
            continue
        row = 1 << bit
        for pivot, value in pivots.items():
            if value >> bit & 1:
                row |= 1 << pivot
        assert all((row & value).bit_count() % 2 == 0 for value in vectors)
        rows.append(row)
    return rows


def read_module(path, index=0):
    doc = json.loads(Path(path).read_text())
    module = doc['candidates'][index] if 'candidates' in doc else doc
    assert isinstance(module.get('operations'), list), path
    return doc, module


def assemble(a_path, bc_path=None, a_index=2, bc_index=0, name='four_measured',
             terminal_start=None, omit_free_cx=False, do_price=False, do_singles=False):
    joint = bc_path is None
    if joint:
        bc_path = a_path
        bc_doc, bc = read_module(bc_path, bc_index)
        a_doc, a = bc_doc, {}
    else:
        a_doc, a = read_module(a_path, a_index)
        bc_doc, bc = read_module(bc_path, bc_index)
    source_stem = Path(a_doc['prefix_stem'])
    if not source_stem.is_absolute():
        source_stem = ROOT / source_stem
    if bc_doc.get('prefix_stem'):
        bc_prefix = Path(bc_doc['prefix_stem'])
        if not bc_prefix.is_absolute():
            bc_prefix = ROOT / bc_prefix
        assert bc_prefix.with_suffix('.qasm').read_bytes() == source_stem.with_suffix('.qasm').read_bytes(), 'Different source prefixes'
    text = source_stem.with_suffix('.qasm').read_text()
    ops, dets = f.parse_current(text)
    ops, dets = copy.deepcopy(ops), copy.deepcopy(dets)
    pc = make_four_square_contract()
    roles = copy.deepcopy(bc_doc.get('roles', bc.get('roles', pc.roles)))
    if a.get('A'):
        assert list(a['A']) == roles['A'], (a['A'], roles['A'])
    D, A, B, C = (roles[k] for k in ('D', 'A', 'B', 'C'))
    assert len(set(D + A + B + C)) == 28
    square_mask = int(bc_doc.get('square_mask', bc.get('square_mask', 29)))
    first_record = max((o.bit for o in ops if o.bit is not None), default=-1) + 1
    next_record = first_record
    assigned = []
    ignored_records = set()
    physical_record_ops = {}
    modules = [('ABC', bc_doc, bc)] if joint else [('A', a_doc, a), ('BC', bc_doc, bc)]
    for label, doc, module in modules:
        ignored_original = set(doc.get('ignore_original_records', module.get('ignore_original_records', [])))
        for row in module['operations']:
            bit = next_record if row['kind'] in ('M', 'MX') else None
            ops.append(f.Op(row['kind'], tuple(row['qs']), int(row['time']), bit))
            if bit is not None:
                if row.get('original_bit') in ignored_original or row.get('record_contract') is False:
                    ignored_records.add(bit)
                if row.get('zero_flag'):
                    dets.append({bit})
                assigned.append(dict(module=label, qubit=row['qs'][0], time=row['time'], kind=row['kind'], bit=bit))
                if row.get('original_bit') is not None:
                    physical_record_ops[row['original_bit']] = dict(time=int(row['time']), kind=row['kind'], qubits=list(row['qs']), bit=bit)
                next_record += 1
    terminal_ops = bc_doc.get('terminal_operations', bc.get('terminal_operations'))
    omitted = sorted(i for i in range(7) if omit_free_cx and not (square_mask >> i & 1))
    if terminal_ops is not None:
        first_touch = {}
        for row in terminal_ops:
            if isinstance(row, dict):
                qs, tick = row['qs'], row['time']
            else:
                _, qs, tick, _ = row
            for q in qs:
                first_touch[q] = min(first_touch.get(q, 10**9), int(tick))
    else:
        first_touch = {q: 0 for q in D + A + B + C}
        for i in omitted:
            first_touch[B[i]], first_touch[C[i]] = 1, 2
    ready = max(o.time + 1 - first_touch[q] for o in ops for q in o.qs if q in first_touch)
    R = ready if terminal_start is None else int(terminal_start)
    assert R >= ready, ('terminal before required resource readiness', R, ready)
    if terminal_ops is not None:
        for row in terminal_ops:
            if isinstance(row, dict):
                kind, qs, tick = row['kind'], row['qs'], row['time']
            else:
                kind, qs, tick, _ = row
            bit = next_record if kind in ('M', 'MX') else None
            ops.append(f.Op(kind, tuple(qs), R + int(tick), bit))
            if bit is not None:
                next_record += 1
    else:
        for i, (d, aa, bb, cc) in enumerate(zip(D, A, B, C)):
            ops.append(f.Op('CX', (d, aa), R))
            if i not in omitted:
                ops.append(f.Op('CX', (bb, cc), R))
            ops.append(f.Op('CX', (bb, d), R + 1))
            if square_mask >> i & 1:
                ops.append(f.Op('CX', (cc, aa), R + 1))
        for block, kind in [(A, 'M'), (B, 'MX'), (C, 'MX')]:
            for q in block:
                ops.append(f.Op(kind, (q,), R + 2, next_record))
                next_record += 1
    seen = {}
    for op in ops:
        if op.kind == 'CX':
            q, r = op.qs
            assert abs(q // 6 - r // 6) + abs(q % 6 - r % 6) == 1, ('non-native CX', op)
        for q in op.qs:
            key = op.time, q
            assert key not in seen, ('physical collision', key, seen.get(key), op)
            seen[key] = op
    ops.sort(key=lambda o: o.time)
    f.DATA = list(D)
    preliminary = emit(ops, dets)
    model = f.make_model(*f.parse_current(preliminary))
    assert not any(r & ignored_records for r in dets), 'An explicitly supplied detector uses an ignored record'
    model.record_ps = {b: p for b, p in model.record_ps.items() if b not in ignored_records}
    contract = complete(model, dets)
    added = [r for r in contract['missing'] if any(b >= first_record for b in r['bits'])]
    assert all(not r['reference'] for r in added), 'Nonzero affine detector reference requires generalized evaluator'
    dets.extend(set(r['bits']) for r in added)
    allowed_faults = [row for doc in (a_doc, bc_doc) for row in doc.get('allow_record_faults', [])]
    mode_receipts = []
    if allowed_faults:
        model = f.make_model(*f.parse_current(emit(ops, dets)))
        vectors = []
        for selector in allowed_faults:
            target = physical_record_ops[selector['original_bit']] if 'original_bit' in selector else selector
            matches = []
            for fault in model.faults:
                op = model.labels[fault['ins']]
                channel = model.chans[fault['chan']]['name']
                if (op.time == target['time'] and op.kind == target['kind']
                        and list(op.qs) == target['qubits']
                        and channel == selector['channel'] and fault['pauli'] == selector['pauli']):
                    matches.append(fault)
            assert len(matches) == 1, (selector, len(matches))
            fault = matches[0]
            assert fault['s'] == 0 and fault['e'] == 0, ('Mode can alter source rotations or output data', selector)
            vectors.append(fault['d'])
            mode_receipts.append(dict(selector=selector, actual_operation=target,
                                      record_flips=fault['record_flips'], detector_sector=fault['d']))
        combined = []
        for mask in null_rows(vectors, len(dets)):
            row = set()
            while mask:
                bit = mask & -mask
                row ^= dets[bit.bit_length() - 1]
                mask ^= bit
            if row:
                combined.append(row)
        dets = combined
    text = emit(ops, dets)
    raw = raw_check(text, D)
    meta = dict(source_prefix=str(source_stem), a_module=str(a_path), a_index=a_index,
                bc_module=str(bc_path), bc_index=bc_index, joint_resource=joint, roles=roles,
                square_mask=square_mask, terminal_start=R, terminal_operations=terminal_ops,
                omitted_free_cx=omitted if terminal_ops is None else None,
                assigned_helper_records=assigned, extra_record_checks=added,
                ignored_record_contract_bits=sorted(ignored_records),
                allowed_record_modes=mode_receipts,
                raw=raw, full_native_assembly=True,
                noise_scope='Full source, preparation, measurement and idle noise; no idealized resources.')
    stem = write_stem(text, D, HERE / 'boundary', name, source=meta)
    result = dict(stem=str(stem), **meta, cx=sum(o.kind == 'CX' for o in ops),
                  ticks=max(o.time for o in ops) + 1, t_gates=sum(o.kind in ('T', 'TDG') for o in ops))
    if raw['ok'] and do_singles:
        result['singles'] = singles(f.make_model(*f.parse_current(text)))
    if raw['ok'] and do_price:
        result['exact'] = price(stem, processes=1)
    stem.with_suffix('.integration.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2), flush=True)
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('a_module')
    ap.add_argument('bc_module', nargs='?', help='Omit for a single joint ABC module.')
    ap.add_argument('--a-index', type=int, default=2)
    ap.add_argument('--bc-index', type=int, default=0)
    ap.add_argument('--name', default='four_measured')
    ap.add_argument('--terminal-start', type=int)
    ap.add_argument('--omit-free-cx', action='store_true')
    ap.add_argument('--price', action='store_true')
    ap.add_argument('--singles', action='store_true')
    args = ap.parse_args()
    assemble(args.a_module, args.bc_module, args.a_index, args.bc_index,
             args.name, args.terminal_start, args.omit_free_cx, args.price, args.singles)
