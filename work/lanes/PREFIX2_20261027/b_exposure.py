"""Diagnose first-order rejection and idle exposure in full native circuits.

This is a diagnostic using the unchanged full-source Pauli evaluator. The
all-orders score remains the ranking criterion. It also exports per-wire idle
weights for fixed-order scheduling: each weight is the rejection probability
of one depolarizing waiting step immediately after that operation.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
from qtools.evaluator import frontend as f


def key(o):
    return o.time, o.kind, tuple(o.qs)


def audit(stem):
    stem = Path(stem)
    text = stem.with_suffix('.qasm').read_text()
    meta = json.loads(stem.with_suffix('.json').read_text())
    f.DATA = meta['data_qubits']
    ops, dets = f.parse_current(text)
    m = f.make_model(ops, dets)
    eng = f.Engine(m)
    cache = {}

    integration = json.loads(stem.with_suffix('.integration.json').read_text())
    source, _ = f.parse_current(Path(integration['source_prefix']).with_suffix('.qasm').read_text())
    regions = {key(o): 'source' for o in source}
    for module, index, label in [('a_module', 'a_index', 'A'), ('bc_module', 'bc_index', 'B')]:
        doc = json.loads(Path(integration[module]).read_text())
        row = doc['candidates'][integration.get(index, 0)] if 'candidates' in doc else doc
        for o in row['operations']:
            regions[o['time'], o['kind'], tuple(o['qs'])] = label

    _, _, gaps = f.schedule(m.native)
    gaps_by_ins = defaultdict(list)
    channels_by_ins = defaultdict(list)
    for ins, q, start, n in gaps:
        gaps_by_ins[ins].append((q, start, n))
    for cid, ch in enumerate(m.chans):
        channels_by_ins[ch['ins']].append(cid)
    idle_channels = {}
    for ins, rows in gaps_by_ins.items():
        for cid, gap in zip(channels_by_ins[ins][-len(rows):], rows):
            ch = m.chans[cid]
            assert ch['name'] == 'DEPOLARIZE1' and ch['qs'] == [gap[0]], (ch, gap)
            idle_channels[cid] = gap

    groups = defaultdict(float)
    wires = defaultdict(float)
    operations = defaultdict(float)
    idle_rows = {}
    axis_rejection = defaultdict(dict)
    c1 = 0.0
    rejection = 0.0
    for fault in m.faults:
        sd = fault['s'], fault['d']
        if sd not in cache:
            cache[sd] = eng.table(*sd)
        out = cache[sd]
        acceptance = 0.0 if out is None else float(out[0])
        weight = fault['p'] / .001
        mass = weight * (1.0 - acceptance)
        rejection += mass
        if out is not None:
            a, ev = out
            c1 += weight * float(.5 * (a - eng.SG[fault['e']] @ ev))
        op = m.labels[fault['ins']]
        region = regions.get(key(op), 'terminal')
        channel = m.chans[fault['chan']]
        idle = idle_channels.get(fault['chan'])
        kind = 'idle' if idle else channel['name']
        groups[region + ':' + kind] += mass
        for q in channel['qs']:
            wires[region + ':' + str(q)] += mass / len(channel['qs'])
        label = f'{region}:{op.time}:{op.kind}:{list(op.qs)}:{kind}'
        operations[label] += mass
        if not idle:
            if op.kind == 'CX' and channel['name'] == 'DEPOLARIZE2':
                for pos, q in enumerate(op.qs):
                    if fault['pauli'][1 - pos] == 'I':
                        axis_rejection[fault['ins'], q][fault['pauli'][pos]] = 1.0 - acceptance
            elif channel['name'] == 'DEPOLARIZE1':
                assert len(channel['qs']) == 1
                axis_rejection[fault['ins'], channel['qs'][0]][fault['pauli']] = 1.0 - acceptance
            elif op.kind in ('R', 'RX'):
                q = op.qs[0]
                axis_rejection[fault['ins'], q] = dict.fromkeys('XYZ', 1.0 - acceptance)
                axis_rejection[fault['ins'], q]['Z' if op.kind == 'R' else 'X'] = 0.0
        if idle:
            q, start, n = idle
            row = idle_rows.setdefault(fault['chan'], dict(
                region=region, preceding_operation=dict(time=op.time, kind=op.kind, qs=list(op.qs), bit=op.bit),
                qubit=q, start=start, length=n, rejection=0.0))
            row['rejection'] += mass
    for row in idle_rows.values():
        row['per_step_rejection'] = row['rejection'] / row['length']
    segment_weights = []
    for (ins, q), axis in axis_rejection.items():
        assert set(axis) == set('XYZ'), (ins, q, axis)
        op = m.labels[ins]
        segment_weights.append(dict(operation=dict(time=op.time, kind=op.kind, qs=list(op.qs)),
                                    qubit=q, rejection=sum(axis.values()) / 3, axis_rejection=axis))
    return dict(stem=str(stem), c1=c1, rejection_coefficient=rejection,
                fault_components=len(m.faults), grouped_rejection=dict(sorted(groups.items())),
                wire_rejection=dict(sorted(wires.items())),
                operation_rejection=dict(sorted(operations.items(), key=lambda r: -r[1])),
                idle_segments=list(idle_rows.values()),
                segment_weights=segment_weights,
                scope='Exact first-order full-source rejection diagnostic, not an all-orders score.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('stems', nargs='+')
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    rows = [audit(s) for s in args.stems]
    out = Path(args.output)
    out.write_text(json.dumps(rows, indent=2) + '\n')
    print(json.dumps([dict(stem=r['stem'], rejection_coefficient=r['rejection_coefficient'],
                           c1=r['c1'], grouped_rejection=r['grouped_rejection']) for r in rows], indent=2))


if __name__ == '__main__':
    main()
