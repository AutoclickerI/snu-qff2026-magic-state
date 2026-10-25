"""INTEG toolkit: native-tick plans of complete circuits, edits, emission.

A plan is dict(h=header lines, ops=[dict(lines, t)], tail=detector lines, meta=json).
Every emitted circuit has one barrier over all used qubits between ticks and is checked
to reproduce its plan ticks natively (official noise schedule).
"""
import os, sys, re, json, copy, hashlib, collections
from pathlib import Path
for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[k] = '1'
sys.dont_write_bytecode = True
H = Path(__file__).resolve().parent
ROOT = H.parents[2]
sys.path[:0] = [str(H), str(ROOT / 'work/lanes/SCHED'), str(ROOT / 'work/lanes/BCSYN2'), str(ROOT / 'work/lanes/FRESH'),
                str(ROOT / 'work/lanes/EVAL'), str(ROOT / 'work')]
import schedule as S
from util import native_times

C = H / 'c'
D = json.loads((H / 'c' / 'baseline.json').read_text())['data_qubits']
BITRE = re.compile(r'c\[(\d+)\]')


class Unit(S.Unit):
    def __init__(self, lines, raw_indices=()):
        if len(lines) == 1 and lines[0].startswith('h '):
            self.lines = lines; self.raw_indices = list(raw_indices); self.name = 'H'
            self.qs = S.name_qs(lines[0])[1]; self.last_is_measure = False
        else:
            super().__init__(lines, list(raw_indices))


S.Unit = Unit


def unit(o):
    return Unit(o['lines'])


def read(stem):
    stem = Path(stem)
    txt = stem.with_suffix('.qasm').read_text()
    h, r, tail = S.qasm_ops(txt)
    u = S.fold_units(r)
    ts = native_times(txt, u)
    return dict(h=h, ops=[dict(lines=x.lines, t=t) for x, t in zip(u, ts)], tail=tail,
                meta=json.loads(stem.with_suffix('.json').read_text()))


def bits_of(o):
    return [int(x) for x in BITRE.findall(' '.join(o['lines']))]


def bit(c):
    return 1 + max(b for o in c['ops'] for b in bits_of(o))


def fix(c):
    c['ops'].sort(key=lambda o: o['t'])
    n = bit(c)
    c['h'] = [re.sub(r'creg c\[\d+\]', f'creg c[{n}]', l) for l in c['h']]
    return c


def normalized(c):
    c = copy.deepcopy(c)
    c['ops'].sort(key=lambda o: o['t'])
    nxt = {}
    for o in reversed(c['ops']):
        u = unit(o)
        if u.name == 'MX' and len(u.lines) == 2 and u.qs[0] in nxt and nxt[u.qs[0]] not in ('RESET', 'RX', 'H'):
            o['lines'].append(f'h q[{u.qs[0]}];')
        for q in u.qs:
            nxt[q] = u.name
    us = [unit(o) for o in c['ops']]
    ts = [o['t'] for o in c['ops']]
    txt = S.emit(c['h'], us, ts, c['tail'])
    h, r, tail = S.qasm_ops(txt)
    nu = S.fold_units(r)
    nt = native_times(txt, nu)
    want = [(t, u.lines) for t, u in zip(S.compress(ts), us)]
    got = [(t, u.lines) for t, u in zip(nt, nu)]
    if want != got:
        bad = [(a, b) for a, b in zip(want, got) if a != b][:6]
        raise ValueError(('native schedule mismatch', bad, len(us), len(nu)))
    for o, u, t in zip(c['ops'], nu, nt):
        o['t'] = t
        if u.name == 'CX':
            a, b = u.qs
            assert abs(a // 6 - b // 6) + abs(a % 6 - b % 6) == 1, o
    c['meta'].update(cx=sum(u.name == 'CX' for u in nu), native_depth=max(nt) + 1)
    return c, txt


def save(c, name, desc=None):
    c, txt = normalized(c)
    st = C / name
    st.with_suffix('.qasm').write_text(txt)
    meta = dict(c['meta'])
    if desc is not None:
        meta['integ'] = desc
    st.with_suffix('.json').write_text(json.dumps(meta, indent=2))
    st.with_suffix('.plan.json').write_text(json.dumps(c))
    return st


def load_plan(name):
    return json.loads((C / name).with_suffix('.plan.json').read_text())


# ---------- detector algebra ----------
def det_rows(c):
    return [set(map(int, BITRE.findall(l))) for l in c['tail'] if l.startswith('// DETECTOR')]


def in_span(c, b):
    piv = {}
    for s in det_rows(c):
        v = sum(1 << x for x in s)
        while v:
            h = v.bit_length() - 1
            if h in piv:
                v ^= piv[h]
            else:
                piv[h] = v
                break
    v = 1 << b
    while v:
        h = v.bit_length() - 1
        if h not in piv:
            return False
        v ^= piv[h]
    return True


def op_of_bit(c, b):
    return next(o for o in c['ops'] if f'-> c[{b}];' in ' '.join(o['lines']))


def drop_bit_from_tail(c, b):
    tail = []
    for line in c['tail']:
        if not line.startswith('// DETECTOR'):
            tail.append(line); continue
        bs = [x for x in map(int, BITRE.findall(line)) if x != b]
        if bs:
            tail.append('// DETECTOR ' + ' '.join(f'c[{x}]' for x in bs))
    c['tail'] = tail


def remove_check(c, b, mode):
    """mode: detector (keep measurement, drop its detector), omit (delete op), reset (replace by reset)."""
    c = copy.deepcopy(c)
    assert in_span(c, b), b
    o = op_of_bit(c, b)
    u = unit(o)
    q = u.qs[0]
    if mode == 'detector':
        line = f'// DETECTOR c[{b}]'
        if line not in c['tail']:
            raise ValueError(('not a singleton detector', b))
        c['tail'].remove(line)
        return c
    if mode == 'omit':
        c['ops'].remove(o)
    elif mode == 'reset':
        o['lines'] = [f'reset q[{q}];'] + ([f'h q[{q}];'] if u.name == 'MX' else [])
    else:
        raise ValueError(mode)
    drop_bit_from_tail(c, b)
    return fix(c)


def seq(c, q):
    return [o for o in sorted(c['ops'], key=lambda o: o['t']) if q in unit(o).qs]


def prep_options(c):
    out = []
    for q in range(36):
        s = seq(c, q)
        for a, b in zip(s, s[1:]):
            u, v = unit(a), unit(b)
            if u.name not in ('RESET', 'RX') or v.name not in ('MEASURE', 'MX') or b['t'] <= a['t'] + 1:
                continue
            if (u.name == 'RX') != (v.name == 'MX'):
                continue
            rec = bits_of(b)[0]
            if in_span(c, rec):
                out.append(dict(q=q, old=a['t'], new=b['t'] - 1, bit=rec, lines=a['lines']))
    return out


def delay_preps(c, selected):
    c = copy.deepcopy(c)
    for r in selected:
        o = next(o for o in c['ops'] if o['t'] == r['old'] and o['lines'] == r['lines'])
        o['t'] = r['new']
    return fix(c)


def busy(c):
    """tick -> set of qubits with an operation at that tick."""
    occ = collections.defaultdict(set)
    for o in c['ops']:
        for q in unit(o).qs:
            occ[o['t']].add(q)
    return occ


def depth(c):
    return 1 + max(o['t'] for o in c['ops'])


def add_ops(c, items):
    c = copy.deepcopy(c)
    for t, lines in items:
        c['ops'].append(dict(t=t, lines=lines))
    return fix(c)


def echo(c, q, h, axis, init, first, last, end, det=True):
    """Echoed parity check on q with fresh helper h: Z axis detects X/Y on q (CX q->h), X axis detects Z/Y (CX h->q)."""
    b = bit(c)
    e = (q, h) if axis == 'Z' else (h, q)
    pre = [f'reset q[{h}];'] + ([f'h q[{h}];'] if axis == 'X' else [])
    post = ([f'h q[{h}];'] if axis == 'X' else []) + [f'measure q[{h}] -> c[{b}];']
    c = add_ops(c, [(init, pre), (first, [f'cx q[{e[0]}],q[{e[1]}];']), (last, [f'cx q[{e[0]}],q[{e[1]}];']), (end, post)])
    if det:
        c['tail'].append(f'// DETECTOR c[{b}]')
    return c


def sha(st):
    return hashlib.sha256(Path(st).with_suffix('.qasm').read_bytes()).hexdigest()
