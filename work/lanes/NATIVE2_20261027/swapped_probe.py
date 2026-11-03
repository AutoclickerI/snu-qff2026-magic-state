"""Assemble the dual old A factory with a connected B probe for fault attribution.

The initial B probe is state-correct but is not assumed hook protected. Its
faults are separated from the new A/source faults in the full official model.
"""
import contextlib
import copy
import io
import json
import argparse
from pathlib import Path
from measured_assemble import assemble, HERE
from old_b_new_a import D, A as CONNECTED, B as SPARSE, C


def build(reverse_order=False):
    adoc = json.loads((HERE / 'dual_old_a_module.json').read_text())
    if reverse_order:
        old = json.loads((HERE.parent / 'END2_20261027/sol/a_only_R47.json').read_text())
        ops = [copy.deepcopy(o) for o in old['operations'] if o['kind'] != 'H']
    else:
        old = json.loads((HERE / 'old_footprint_a_s1.json').read_text())['candidates'][0]
        assert old['direct'] and not old['helpers']
        ops = copy.deepcopy(old['operations'])
        for q in CONNECTED:
            last = max(o['time'] for o in ops if q in o['qs'])
            ops.append(dict(kind='H', qs=[q], time=last + 1))
    term = [('CX', [d, a], int(reverse_order), None) for d, a in zip(D, SPARSE)]
    term += [('CX', [b, d], 1 - int(reverse_order), None) for b, d in zip(CONNECTED, D)]
    term += [('M', [q], 2, i) for i, q in enumerate(SPARSE)]
    term += [('MX', [q], 2, 7 + i) for i, q in enumerate(CONNECTED)]
    bdoc = dict(prefix_stem=adoc['prefix_stem'], roles=dict(D=D, A=SPARSE, B=CONNECTED, C=C),
                square_mask=0, terminal_operations=term,
                candidates=[dict(operations=ops, resource_ready=max(o['time'] for o in ops) + 1)],
                scope='State-correct connected B probe; no hook protection claim.')
    tag = 'swapped_reverse_probe' if reverse_order else 'swapped_probe'
    path = HERE / f'{tag}_b_module.json'
    path.write_text(json.dumps(bdoc, indent=2) + '\n')
    with contextlib.redirect_stdout(io.StringIO()):
        result = assemble(HERE / 'dual_old_a_module.json', path, 0, 0,
                          tag, do_singles=True)
    bkeys = {(o['time'], tuple(o['qs']), o['kind']) for o in ops}
    akeys = {(o['time'], tuple(o['qs']), o['kind']) for o in adoc['candidates'][0]['operations']}
    split = {'B_probe': [], 'dual_A': [], 'source_or_terminal': []}
    for fault in result.get('singles', {}).get('harmful_faults', []):
        key = fault['time'], tuple(fault['qubits']), fault['operation']
        kind = 'B_probe' if key in bkeys else 'dual_A' if key in akeys else 'source_or_terminal'
        split[kind].append(fault)
    out = dict(stem=result['stem'], raw=result['raw'], cx=result['cx'], ticks=result['ticks'],
               c1=result.get('singles', {}).get('c1'),
               contributions={k: sum(f['c1_contribution'] for f in fs) for k, fs in split.items()},
               faults_by_module=split,
               scope='Complete native probe with deliberately unverified connected B. No winner claim.')
    (HERE / f'{tag}_result.json').write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: v for k, v in out.items() if k != 'faults_by_module'}, indent=2), flush=True)
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--reverse-order', action='store_true')
    args = ap.parse_args()
    build(args.reverse_order)
