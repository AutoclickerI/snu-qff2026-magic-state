"""Replace v36c's B/C resource preparation with a new one (layered units, one barrier per native step).

prep spec: {"inits": {q: [kind, tick]}, "cx": [[tick, u, v], ...]}; kind in R, M, RX, MX.
Old prep inits/CX (bcspec 'prep') are removed with their literal init detectors and their pivot frame bits;
new M inits get literal detectors; new MX pivot records are folded into every detector through Pauli frames.
"""
import sys, json, re
from pathlib import Path
from qcirc import parse, emit, adjacent
from decompose import split, is_round

D = [0, 20, 7, 10, 3, 22, 21]
A = [1, 14, 8, 9, 2, 16, 15]
B = [6, 26, 13, 11, 4, 23, 27]
C = [12, 25, 19, 17, 5, 29, 28]
BC = set(B + C)
HERE = Path(__file__).resolve().parent


def load(stem):
    units, dets = parse(Path(stem).with_suffix('.qasm').read_text())
    return units, dets


def prep_indices(units):
    life_of, find, entry, comp = split(units)
    pre = set()
    for root, idx in comp.items():
        if root in entry:
            pre |= set(idx)
    out = []
    for i, u in enumerate(units):
        qs, t, k = set(u['q']), u['t'], u['k']
        if i in pre or not (qs <= BC) or t < 32 or t >= 44:
            continue
        out.append(i)
    return out


def extract(units):
    """The prep spec of a circuit (inits = last init per BC cell, plus any extra units kept verbatim)."""
    idx = prep_indices(units)
    inits, cx, extra = {}, [], []
    for i in idx:
        u = units[i]
        if u['k'] == 'CX':
            cx.append([u['t'], u['q'][0], u['q'][1]])
        else:
            q = u['q'][0]
            if q in inits:
                extra.append([inits[q][1], inits[q][0], q])
            inits[q] = [u['k'], u['t']]
    return dict(inits={str(q): v for q, v in inits.items()}, cx=cx, extra=extra)


def frames_corrections(units, sources):
    """Pauli-frame propagation of record bits from `sources` {unit index: (q, bit)} (MX init -> Z frame).
    Returns {record bit: set of source bits that flip it}."""
    fr = {}
    corr = {}
    for i in sorted(range(len(units)), key=lambda i: (units[i]['t'], i)):
        u = units[i]
        k = u['k']
        if i in sources:
            q, b = sources[i]
            fr[q] = [set(), {b}]
            continue
        if k in ('R', 'RX'):
            fr[u['q'][0]] = [set(), set()]
        elif k == 'CX':
            a, b = u['q']
            fa = fr.setdefault(a, [set(), set()]); fb = fr.setdefault(b, [set(), set()])
            fb[0] ^= fa[0]; fa[1] ^= fb[1]
        elif k in ('M', 'MX'):
            q = u['q'][0]
            f = fr.setdefault(q, [set(), set()])
            c = f[1] if k == 'MX' else f[0]
            if c:
                corr[u['b']] = set(c)
            if k == 'M':
                # Z measurement collapses X-frame? the frame stays (state |m xor frame>); keep
                pass
        elif k in ('T', 'TDG'):
            q = u['q'][0]
            if q in fr and (fr[q][0]):
                raise AssertionError(('X frame through T', u))
    return corr, fr


def prep_by_keys(units, ref_units, also=(), absent=()):
    """Indices of `units` matching the reference circuit's prep units (t, kind, qubits) except the `absent`
    keys, plus keys in `also`."""
    keys = {(ref_units[i]['t'], ref_units[i]['k'], tuple(ref_units[i]['q'])) for i in prep_indices(ref_units)}
    assert set(absent) <= keys, absent
    keys = (keys - set(absent)) | set(also)
    out = [i for i, u in enumerate(units) if (u['t'], u['k'], tuple(u['q'])) in keys]
    assert len(out) == len(keys), (len(out), len(keys))
    return out


def build(base_units, base_dets, spec, data=D, old=None):
    units = [dict(u) for u in base_units]
    dets = [list(d) for d in base_dets]
    old = set(prep_indices(units) if old is None else old)
    old_init_bits_M = {units[i]['b'] for i in old if units[i]['k'] == 'M'}
    old_init_bits_MX = {units[i]['b'] for i in old if units[i]['k'] == 'MX'}
    nd = []
    for d in dets:
        s = set(d)
        if s & old_init_bits_M:
            assert len(s) == 1, ('init detector not literal', d)
            continue
        s -= old_init_bits_MX
        assert s, d
        nd.append(sorted(s))
    keep = [u for i, u in enumerate(units) if i not in old]
    nbits = max(max([u['b'] for u in units if u['b'] is not None]) + 1, 0)
    newu = []
    sources = {}
    newdets = []
    extra = spec.get('extra', [])
    for t, k, q in extra:
        u = dict(k=k, q=(q,), t=t, b=None)
        if k in ('M', 'MX'):
            u['b'] = nbits; nbits += 1
            if k == 'M':
                newdets.append([u['b']])
            else:
                u['src'] = (q, u['b'])
        newu.append(u)
    for qs, (k, t) in spec['inits'].items():
        q = int(qs)
        u = dict(k=k, q=(q,), t=t, b=None)
        if k in ('M', 'MX'):
            u['b'] = nbits; nbits += 1
            if k == 'M':
                newdets.append([u['b']])
            else:
                u['src'] = (q, u['b'])
        newu.append(u)
    for t, a, b in spec['cx']:
        assert adjacent(a, b), (a, b)
        newu.append(dict(k='CX', q=(a, b), t=t, b=None))
    # a flag readout M at the tick of an existing reset on that helper replaces the reset (M leaves |0>)
    mq = {(u['t'], u['q'][0]) for u in newu if u['k'] == 'M'}
    keep = [u for u in keep if not (u['k'] == 'R' and (u['t'], u['q'][0]) in mq)]
    allu = keep + newu
    sources = {i: u.pop('src') for i, u in enumerate(allu) if 'src' in u}
    # one unit per qubit per step
    seen = {}
    for u in allu:
        for q in u['q']:
            key = (u['t'], q)
            assert key not in seen, ('collision', u, seen[key])
            seen[key] = u
    corr, fr = frames_corrections(allu, sources)
    for q in data:
        assert not any(fr.get(q, [set(), set()])), ('frame on data', q, fr.get(q))
    out = []
    for d in nd + newdets:
        s = set(d)
        ex = set()
        for b in d:
            ex ^= corr.get(b, set())
        out.append(sorted(s ^ ex))
    return allu, out, nbits


def write(stem, units, dets, nbits, meta=None):
    stem = Path(stem)
    stem.with_suffix('.qasm').write_text(emit(units, dets, nbits))
    m = dict(data_qubits=D, cx=sum(u['k'] == 'CX' for u in units), native_depth=max(u['t'] for u in units) + 1)
    if meta:
        m.update(meta)
    stem.with_suffix('.json').write_text(json.dumps(m, indent=1) + '\n')


if __name__ == '__main__':
    bu, bd = load(HERE / 'v36c')
    spec = extract(bu)
    print(json.dumps(spec))
    u, d, nb = build(bu, bd, spec)
    write(HERE / 'cand' / 'v36c_resplice', u, d, nb)
