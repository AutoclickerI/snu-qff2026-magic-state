"""Construct and audit a B-ready45 candidate with explicit source advances.

The q28, q4 and q5 source edits preserve per-wire operation order and gate
counts. The initial B CX3->4 is omitted as a candidate state-dependent identity;
the full raw and mixed-Pauli audits decide whether that omission is valid.
"""
import os
for key in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[key] = '1'
import contextlib
import copy
import io
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'work/tools'))
sys.path.insert(0, str(ROOT / 'work/lanes/END2_20261027'))
sys.path.insert(0, str(ROOT / 'work/lanes/NATIVE2_20261027'))
from qtools import write_stem
from qtools.evaluator import frontend as f
from qtools.validity import raw_check
from joint import emit
from measured_assemble import assemble
from b_schedule import schedule
from pairs import audit as pair_audit


def earliest_chain(ops, release, targets):
    free = {q: (t, dict(source_qubit=q, release=t)) for q, t in release.items()}
    rows = []
    for i, o in enumerate(ops):
        time, cause = max((free[q] for q in o['qs']), key=lambda r: r[0])
        rows.append(dict(operation=o, earliest=time, predecessor=cause))
        for q in o['qs']:
            free[q] = time + 1, i
    finish, cause = max((free[q] for q in targets), key=lambda r: r[0])
    chain = []
    while isinstance(cause, int):
        chain.append(rows[cause])
        cause = rows[cause]['predecessor']
    return dict(ready=finish, source=cause, chain=list(reversed(chain)))


def main():
    adoc = json.loads((ROOT / 'work/lanes/NATIVE2_20261027/strong48_cp_native_m9_a_module.json').read_text())
    bdoc = json.loads((HERE / 'retimed/strong48_m9_b_reject46.json').read_text())
    assert adoc['prefix_stem'] == bdoc['prefix_stem']
    parent = Path(adoc['prefix_stem'])
    ops, dets = f.parse_current(parent.with_suffix('.qasm').read_text())
    old_wire_orders = {q: [(o.kind, o.qs, o.bit) for o in ops if q in o.qs] for q in range(36)}
    changes = []

    def move(kind, qs, t, nt):
        found = [o for o in ops if o.kind == kind and o.qs == tuple(qs) and o.time == t]
        assert len(found) == 1, (kind, qs, t, len(found))
        found[0].time = nt
        changes.append(dict(kind=kind, qs=qs, old_time=t, new_time=nt, bit=found[0].bit))

    # Moving in ascending order is unambiguous because every new time is lower.
    move('R', [28], 21, 20)
    for t in (22, 23, 24, 25, 26, 28, 29):
        move('CX', [28, 22], t, t - 1)
    move('M', [28], 27, 26)
    move('CX', [4, 5], 32, 31)
    move('CX', [4, 10], 33, 32)
    move('M', [5], 33, 32)
    move('M', [5], 34, 33)
    move('MX', [4], 34, 33)
    occupied = set()
    for o in ops:
        for q in o.qs:
            assert (o.time, q) not in occupied, ('source collision', o)
            occupied.add((o.time, q))
    ops.sort(key=lambda o: o.time)
    assert all([(o.kind, o.qs, o.bit) for o in ops if q in o.qs] == old_wire_orders[q] for q in range(36))
    text = emit(ops, dets)
    data = bdoc['roles']['D']
    raw = raw_check(text, data)
    assert raw['ok'], raw
    source = write_stem(text, data, HERE / 'retimed', 'b45_source',
                        source=dict(parent=str(parent), changes=changes, raw=raw))
    release = {q: max((o.time for o in ops if q in o.qs), default=-1) + 1 for q in range(36)}
    adoc['prefix_stem'] = bdoc['prefix_stem'] = str(source)
    old = bdoc['candidates'][0]['operations']
    removed = [o for o in old if o['kind'] == 'CX' and o['qs'] == [3, 4] and o.get('original_time') == 39]
    assert len(removed) == 1
    bdoc['candidates'][0]['operations'] = [o for o in old if o not in removed]
    bdoc['candidates'][0]['removed_state_identity'] = removed
    a_path = HERE / 'retimed/b45_a_module.json'
    b_path = HERE / 'retimed/b45_unscheduled_b_module.json'
    a_path.write_text(json.dumps(adoc, indent=2) + '\n')
    b_path.write_text(json.dumps(bdoc, indent=2) + '\n')
    chain = earliest_chain(bdoc['candidates'][0]['operations'], release, bdoc['roles']['B'])
    result = dict(source=str(source), source_changes=changes, source_raw=raw,
                  source_preserves_all_wire_orders=True,
                  removed_b_operation=removed, earliest_wire_order=chain)
    try:
        scheduled = schedule(b_path, ready=45, end=46, name='b45_alap_b_module')
    except AssertionError as exc:
        result['schedule_status'] = 'INFEASIBLE within unchanged per-wire order'
        result['failure'] = str(exc)
    else:
        result.update(schedule_status='FEASIBLE', a_module=str(a_path), b_module=str(scheduled))
        with contextlib.redirect_stdout(io.StringIO()):
            full = assemble(a_path, scheduled, 0, 0, 'b45_with48A', do_singles=True)
            if full['raw']['ok'] and full['singles']['c1'] < 1e-10:
                full['pairs'] = pair_audit(full['stem'], HERE / 'retimed/b45_with48A.pairs.json')
        result['full'] = full
    receipt = HERE / 'retimed/b45_result.json'
    receipt.write_text(json.dumps(result, indent=2) + '\n')
    summary = {k: result[k] for k in ('schedule_status', 'source', 'a_module', 'b_module', 'failure') if k in result}
    summary['earliest_ready'] = chain['ready']
    if 'full' in result:
        full = result['full']
        summary['full'] = {k: full.get(k) for k in ('stem', 'raw', 'cx', 'ticks', 'singles')}
        summary['full']['c2'] = full.get('pairs', {}).get('c2')
    summary['receipt'] = str(receipt)
    print(json.dumps(summary, indent=2), flush=True)


if __name__ == '__main__':
    main()
