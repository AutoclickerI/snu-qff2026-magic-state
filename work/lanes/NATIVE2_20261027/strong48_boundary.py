"""A concrete 48-tick strong-A experiment with changed source postselection.

The source loses its standalone M9 and M15 heralds so their physical cells can
enter the stronger A instrument one tick sooner. This is an explicit physical
experiment, not a claim of baseline-equivalent acceptance. The completed
instrument and the incumbent's two benign B record modes are derived afresh.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import argparse
import contextlib
import copy
import io
import json
import sys
from pathlib import Path

from measured_assemble import HERE, ROOT, assemble
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/END2_20261027'))
sys.path.insert(0, str(ROOT / 'work/lanes/PREFIX2_20261027'))
from qtools import write_stem
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from joint import emit
from pairs import audit


def official_q9_receipt(text):
    from tprep.qasm import convert
    from tprep.noise import schedule, noise_blocks
    native, _, errors = convert(text)
    assert not errors, errors
    prog, steps, _ = schedule(native)
    _, blocks = noise_blocks(native, 0.001)
    selected = []
    for ins, places, block in zip(prog, steps, blocks):
        if 9 not in ins.qubits:
            continue
        tick = next(t for qs, t in places if 9 in qs)
        if tick < 38:
            continue
        selected.append(dict(kind=ins.name, qs=list(ins.qubits), time=tick,
                             noise_block=[line.split('#')[0].strip() for line in block]))
    assert [(r['kind'], r['time']) for r in selected[:2]] == [('H', 38), ('MX', 39)], selected
    assert 'DEPOLARIZE1(0.001) 9' in selected[0]['noise_block'], selected
    return dict(format_errors=errors, q9_native_operations=selected,
                scope='Official tprep.qasm.convert and tprep.noise schedule/noise_blocks, unmodified.')


def build(name='strong48_boundary', do_pairs=False, do_price=False, preserve_m9=False):
    bpath0 = ROOT / 'work/lanes/PREFIX2_20261027/retimed/old_b_cut2_jit.json'
    bdoc = json.loads(bpath0.read_text())
    original = Path(bdoc['prefix_stem'])
    ops, dets = f.parse_current(original.with_suffix('.qasm').read_text())
    ops, dets = copy.deepcopy(ops), copy.deepcopy(dets)
    edits = []

    def find(kind, qs, tick):
        matches = [o for o in ops if o.kind == kind and o.qs == tuple(qs) and o.time == tick]
        assert len(matches) == 1, (kind, qs, tick, matches)
        return matches[0]

    def remove_record(bit):
        nonlocal dets
        before = [sorted(row) for row in dets if bit in row]
        dets = [row - {bit} for row in dets if row - {bit}]
        return before

    m15 = find('M', [15], 40)
    ops.remove(m15)
    edits.append(dict(action='remove', kind='M', qs=[15], time=40, bit=m15.bit,
                      removed_record_from_checks=remove_record(m15.bit)))
    m9 = find('M', [9], 39)
    if preserve_m9:
        gate9 = find('CX', [9, 10], 38)
        gate9.kind, gate9.qs = 'H', (9,)
        m9.kind = 'MX'
        edits.append(dict(action='replace', old_kind='CX', old_qs=[9, 10], new_kind='H', qs=[9], time=38,
                          note='Standalone H is one noisy clock; data10 idles honestly.'))
        edits.append(dict(action='replace', old_kind='M', new_kind='MX', qs=[9], time=39, retained_bit=m9.bit))
    else:
        removed_bit = m9.bit
        m9.kind, m9.bit = 'RX', None
        edits.append(dict(action='replace', old_kind='M', new_kind='RX', qs=[9], time=39,
                          removed_bit=removed_bit, removed_record_from_checks=remove_record(removed_bit)))
    m7 = find('M', [7], 40)
    m7.time = 39
    edits.append(dict(action='move', kind='M', qs=[7], time=40, new_time=39, bit=m7.bit))
    last13 = find('CX', [13, 19], 39)
    ops.remove(last13)
    edits.append(dict(action='remove', kind='CX', qs=[13, 19], time=39))
    m13 = find('M', [13], 40)
    m13.time = 39
    edits.append(dict(action='move', kind='M', qs=[13], time=40, new_time=39, bit=m13.bit))
    seen = set()
    for op in ops:
        for q in op.qs:
            assert (op.time, q) not in seen, ('Source collision', op)
            seen.add((op.time, q))
    ops.sort(key=lambda o: o.time)
    data = bdoc['roles']['D']
    text = emit(ops, dets)
    raw = raw_check(text, data)
    assert raw['ok'], raw
    policy = ('Changed source postselection: remove standalone source M15 herald; retain c321 via noisy H38 then native MX39.' if preserve_m9 else
              'Changed source postselection: remove standalone source M9 and M15 heralds.')
    native_receipt = official_q9_receipt(text) if preserve_m9 else None
    source = write_stem(text, data, HERE / 'boundary', name + '_source',
                        source=dict(parent=str(original), edits=edits, raw=raw,
                                    acceptance_policy=policy))
    adoc = json.loads((HERE / 'compact_a_modes_no8_jit_a_module.json').read_text())
    adoc['prefix_stem'] = str(source)
    aops = adoc['candidates'][0]['operations']
    for row in aops:
        row['time'] -= 1
    duplicated = [row for row in aops if row['kind'] == 'RX' and row['qs'] == [9] and row['time'] == 39]
    assert len(duplicated) == 1
    aops.remove(duplicated[0])
    adoc.update(scope='Strong 11CX A preparation and logical-X readout shifted one tick earlier; plus9 supplied by changed source.',
                source_edits=edits,
                acceptance_policy=policy + ' Retain both baseline-accepted B record modes using physical fault projection.')
    bdoc['prefix_stem'] = str(source)
    apath = HERE / f'{name}_a_module.json'
    bpath = HERE / f'{name}_b_module.json'
    apath.write_text(json.dumps(adoc, indent=2) + '\n')
    bpath.write_text(json.dumps(bdoc, indent=2) + '\n')
    with contextlib.redirect_stdout(io.StringIO()):
        result = assemble(apath, bpath, 0, 0, name, terminal_start=46,
                          do_singles=True, do_price=do_price)
    result.update(source_edits=edits, source_raw=raw,
                  acceptance_policy=adoc['acceptance_policy'])
    if preserve_m9:
        result['official_q9_source_receipt'] = native_receipt
        result['official_q9_full_receipt'] = official_q9_receipt(Path(result['stem']).with_suffix('.qasm').read_text())
    if do_pairs and result['raw']['ok'] and result['singles']['c1'] < 1e-12:
        with contextlib.redirect_stdout(io.StringIO()):
            pairs = audit(result['stem'], HERE / f'{name}.pairs.json')
        result['c2'] = pairs['c2']
    (HERE / f'{name}.result.json').write_text(json.dumps(result, indent=2) + '\n')
    summary = {k: result[k] for k in ('stem', 'source_raw', 'raw', 'cx', 'ticks', 'singles', 'c2', 'exact') if k in result}
    print(json.dumps(summary, indent=2), flush=True)
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--name', default='strong48_boundary')
    ap.add_argument('--pairs', action='store_true')
    ap.add_argument('--price', action='store_true')
    ap.add_argument('--preserve-m9', action='store_true')
    args = ap.parse_args()
    build(args.name, args.pairs, args.price, args.preserve_m9)
