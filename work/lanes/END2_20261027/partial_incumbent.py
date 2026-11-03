"""Actual v37j incoming state with an instantaneous ideal terminal resource.

Four explicit ideal encoder ticks are inserted after prefix tick 44. They have
zero noise, and their extra data-wait duration is removed from the exact idle
channels. Thus the first terminal layer is physically the tick after 44 in
this diagnostic. The circuit file itself is not a submission candidate.
"""
import argparse
import json
import sys
from pathlib import Path
from partial_square import A, B, C, D, HERE, ROOT, emit, f, prep, prep_shortened_c, ideal_contract_check, sw
from record_contract import complete


def build(mask, compensated=False):
    ops, ds = f.parse_current((ROOT / 'work/lanes/MAIN/v37j.qasm').read_text())
    source = next(o for o in ops if o.bit == 366)
    source.kind, source.bit = 'R', None
    prefix = [o for o in ops if o.time <= 44]
    bits = {o.bit for o in prefix if o.bit is not None}
    dets = [r - {366} for r in ds if r - {366} and r - {366} <= bits]
    ops = prefix[:]
    for block, plus in [(A, True), (B, False)]:
        prep(ops, block, 45, plus)
    if compensated:
        assert mask == 63
        prep_shortened_c(ops, 45)
        # An additional ideal layer (tick49) implements the correlated B/C
        # boundary. All later layers move once, and its artificial idle time
        # is excluded by the recorded counterfactual selector below.
        ops.extend(f.Op('CX', (b,c), 49) for b,c in zip(B,C))
    else:
        prep(ops, C, 45, True)
    shift = int(compensated)
    for i in range(7):
        ops.extend([f.Op('CX', (D[i], A[i]), 49+shift), f.Op('CX', (B[i], C[i]), 49+shift),
                    f.Op('CX', (B[i], D[i]), 50+shift)])
        if mask >> i & 1:
            ops.append(f.Op('CX', (C[i], A[i]), 50+shift))
    for offset, block, kind in [(400, A, 'M'), (407, B, 'MX'), (414, C, 'MX')]:
        ops.extend(f.Op(kind, (q,), 51+shift, offset + i) for i, q in enumerate(block))
    text = emit(ops, dets)
    f.DATA = D
    model = f.make_model(*f.parse_current(text))
    rec = complete(model, dets)
    extra = [r for r in rec['missing'] if any(b >= 400 for b in r['bits'])]
    assert not any(r['reference'] for r in extra), extra
    dets += [set(r['bits']) for r in extra]
    text = emit(ops, dets)
    raw = ideal_contract_check(text, D)
    stem = HERE / 'counterfactual' / f'incumbent_partial_{mask:02x}{"_compensated" if compensated else ""}'
    stem.with_suffix('.qasm').write_text(text)
    stem.with_suffix('.json').write_text(json.dumps(dict(data_qubits=D, ideal_contract=raw, gate_valid=False, square_mask=mask,
        compensated=compensated, inserted_ticks=list(range(45,49+shift)),
        diagnostic_only=True, source='v37j through tick44 with c366 fixed at source',
        resource_preparation=f'Ideal nonlocal preparation at inserted ticks45..{48+shift}; remove its added waiting duration.',
        resource_state='A plusL; B zeroL; C span(012,034,135,6); conjugate B/C by transversal B->C' if compensated else 'A,C plusL; B zeroL',
        actual_terminal_times=[45, 46, 47], resource_contract=extra), indent=2) + '\n')
    return stem


def diagnose(stem):
    meta = json.loads(stem.with_suffix('.json').read_text())
    if not meta['ideal_contract']['ok']:
        print(json.dumps(meta['ideal_contract']), flush=True)
        return
    m, eng, groups, nd, ks, psi, where, _ = sw.prepare(stem, True)
    inserted_ticks = set(meta['inserted_ticks'])
    removed, resized = [], []
    for cid, ch in enumerate(m.chans):
        if m.labels[ch['ins']].time in inserted_ticks:
            ch['p'] = 0
            for ff in groups[cid]:
                ff['p'] = 0
            removed.append(cid)
    # Keep the noisy causal prefix and terminal. Remove only the artificial
    # elapsed time allocated to the ideal, instantaneous replacement resource.
    _, _, gaps = f.schedule(m.native)
    for ins, q, start, n in gaps:
        removed_ticks = len(set(range(start, start + n)) & inserted_ticks)
        if not removed_ticks or m.labels[ins].time in inserted_ticks:
            continue
        matches = [(cid, ch) for cid, ch in enumerate(m.chans)
                   if ch['ins'] == ins and ch['qs'] == [q] and ch['name'] == 'DEPOLARIZE1']
        assert matches, (ins, q, start, n)
        cid, ch = max(matches, key=lambda item: item[1]['jl'])
        old = ch['p']
        assert abs(old - .75 * (1 - (1 - 4 * .001 / 3) ** n)) < 1e-12, (old, n)
        ch['p'] = .75 * (1 - (1 - 4 * .001 / 3) ** (n - removed_ticks))
        for ff in groups[cid]:
            ff['p'] = ch['p'] / 3
        resized.append(dict(channel=cid, qubit=q, source_time=m.labels[ins].time,
                            old_wait=n, retained_wait=n - removed_ticks, old_p=old, new_p=ch['p']))
    cache = {}
    first = 0.
    harmful = []
    for ff in m.faults:
        if not ff['p']:
            continue
        key = ff['s'], ff['d']
        if key not in cache:
            cache[key] = eng.ntable(*key)
        _, n = cache[key]
        val = 0. if n is None else max(0., float(n[ff['e']]))
        first += ff['p'] / .001 * val
        if val > 1e-10:
            o = m.labels[ff['ins']]
            harmful.append(dict(time=o.time, kind=o.kind, qubits=o.qs, pauli=ff['pauli'], numerator=val))
    out = dict(stem=str(stem.relative_to(ROOT)), ideal_contract=meta['ideal_contract'],
        single_fault_numerator=first, harmful_single_components=harmful,
        ideal_preparation_channels=removed, removed_artificial_idle=resized,
        scope='Noisy v37j history through44; perfect instantaneous resource at45; source c366 fixed; preparation and extra-duration noise excluded.',
        resource_state=meta['resource_state'], square_mask=meta['square_mask'])
    print('single', json.dumps({k: v for k, v in out.items() if k not in ('ideal_preparation_channels', 'removed_artificial_idle', 'harmful_single_components')}), flush=True)
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
    print(json.dumps({k: v for k, v in out.items() if k not in ('ideal_preparation_channels', 'removed_artificial_idle', 'harmful_single_components')}), flush=True)
    return out


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--masks', default='63,127')
    args = ap.parse_args()
    for mask in map(int, args.masks.split(',')):
        diagnose(build(mask))
