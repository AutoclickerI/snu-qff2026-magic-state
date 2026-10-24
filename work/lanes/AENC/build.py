"""Build a complete circuit: v36c with block A's encoder region replaced by an enc.py spec.

Region ops removed: every op on A cells strictly between a cell's release measurement and its D->A CX
(inits, the q16 MX check, encoder CX). Optional `drop`: release measurements removed (hop source checks),
with their detector rows. New MX checks get fresh record bits and single-bit detector rows.
"""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work/lanes/T14')
import qcirc
from bmodel import A, POS, DA
import bmodel

V36C = Path('/home/jihoon/competitions/quantumn/work/lanes/MAIN/v36c')
RELM = {1: (37, 64), 2: (35, 67), 8: (35, 54), 9: (37, 56), 14: (36, 12), 15: (39, 57), 16: (37, 55)}


def build(spec, stem, drop=(), base=V36C, meta=None):
    units, dets = qcirc.parse(Path(base).with_suffix('.qasm').read_text())
    data = json.loads(Path(base).with_suffix('.json').read_text())['data_qubits']
    keep, removed_bits = [], set()
    for u in units:
        qs = u['q']
        if all(q in POS for q in qs) and all(RELM[q][0] < u['t'] < DA[q] for q in qs):
            if u['b'] is not None: removed_bits.add(u['b'])
            continue
        if len(qs) == 1 and qs[0] in drop and u['k'] == 'M' and u['b'] == RELM[qs[0]][1] and u['t'] == RELM[qs[0]][0]:
            removed_bits.add(u['b'])
            continue
        keep.append(u)
    nbits = max([u['b'] for u in units if u['b'] is not None]) + 1
    newdets = [d for d in dets if not (set(d) & removed_bits)]
    pos_of = {tuple(d): i for i, d in enumerate(dets)}
    assert all(not (set(d) & removed_bits) or len(d) == 1 for d in dets), 'a removed record sits in a multi-bit row'
    for q, (k, t) in spec['init'].items():
        if k in ('R', 'RX'):
            keep.append(dict(k=k, q=(q,), t=t, b=None))
        elif k == 'MR':
            assert q not in drop
        elif k == 'U':          # unmeasured hop source used directly
            assert q in drop
    free = sorted(b for b in removed_bits if b not in {RELM[q][1] for q in drop})
    for t, q in spec.get('checks', []):
        if free:
            b = free.pop(0)
        else:
            b = nbits; nbits += 1
        keep.append(dict(k='MX', q=(q,), t=t, b=b))
        newdets.append([b])
    for t, c, g in spec['cx']:
        keep.append(dict(k='CX', q=(c, g), t=t, b=None))
    keep.sort(key=lambda u: u['t'])
    m = dict(source='AENC build on v36c', encoder=dict(init={str(q): v for q, v in spec['init'].items()},
                                                       cx=spec['cx'], checks=spec.get('checks', [])), dropped=list(drop))
    if meta: m.update(meta)
    m['R'] = 44
    qcirc.save(stem, keep, newdets, data, meta=m, nbits=nbits)
    return Path(stem)


if __name__ == '__main__':
    import enc
    out = build(enc.V36C, HERE / 'cand' / 'rebuild_v36c')
    a = (HERE / 'cand' / 'rebuild_v36c.qasm').read_text()
    b = V36C.with_suffix('.qasm').read_text()
    print('identical qasm' if a == b else 'qasm differs', len(a), len(b))
