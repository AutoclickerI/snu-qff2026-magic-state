import json
import re
import sys
from pathlib import Path

ROOT = Path('/home/jihoon/competitions/quantumn')
OUT = ROOT / 'work/lanes/PRE2'
sys.path.insert(0, str(ROOT / 'work'))
sys.path.insert(0, str(ROOT / 'work/lanes/DR'))
import cultiv_port
import merge as dm

V14 = ROOT / 'work/candidates/v14_bcm.qasm'
PREPS = {
    'a': ROOT / 'work/lanes/DR/prepA_L5_s7307.json',
    'bc': ROOT / 'work/lanes/ST_BC/prepBC_L5_best.json',
}
COMPACT_BC = ROOT / 'work/lanes/BC2/compact_base_d13_k82.prep.json'


def v14_prefix(narrow=False, nobar=False, active=False):
    lines = V14.read_text().splitlines()
    # v14's cultivation prefix ends at its final barrier (QASM line 204).
    # Lines 205 onward are the already-merged data moves/block preps.
    end = 204
    raw = lines[:end]
    if narrow or nobar or active:
        used = sorted({int(q) for s in raw for q in re.findall(r'q\[(\d+)\]', s)
                       if not s.startswith(('barrier', 'qreg')) and int(q) < 36})
        bar = 'barrier ' + ','.join(f'q[{q}]' for q in used) + ';'
        out, layer = [], []
        for s in raw:
            if s.startswith('barrier'):
                if nobar:
                    out.append('')
                elif active:
                    qs = sorted({int(q) for x in layer for q in re.findall(r'q\[(\d+)\]', x)})
                    out.append('barrier ' + ','.join(f'q[{q}]' for q in qs) + ';' if qs else '')
                else:
                    out.append(bar)
                layer = []
            else:
                out.append(s)
                if s.strip() and not s.startswith(('OPENQASM', 'include', 'qreg', 'creg', '//')):
                    layer.append(s)
        raw = out
    return '\n'.join(raw) + '\n'


def cp_prefix(stages=('inject', 'check'), full_barrier=False):
    c = cultiv_port.build(stages=stages, s_to='Tswap')
    text = c.rescheduled(lazy_init=True).text()
    if full_barrier:
        used = list(range(36))
        # Keep q[18], q[24], q[30..35] out: the baseline uses the 30 cells
        # that its merged circuit can address.
        used = [q for q in range(36) if q not in (18, 24, 30, 31, 32, 33, 34, 35)]
        text = re.sub(r'^barrier .*?;$', 'barrier ' + ','.join(f'q[{q}]' for q in used) + ';', text, flags=re.M)
    return text


def write_prefix(name, text):
    p = OUT / (name + '_prefix.qasm')
    p.write_text(text)
    return p


def merge(name, prefix, compact=False):
    dm.PREFIX = str(prefix)
    dm.CUT = len(prefix.read_text().splitlines()) + 1
    preps = {k: json.loads(p.read_text()) for k, p in PREPS.items()}
    if compact:
        preps['bc'] = json.loads(COMPACT_BC.read_text())
    text, data, R, pend = dm.build(preps, ['a', 'bc'], dm.LAYOUTS['L5'], dm.MOVES['L5'])
    q = OUT / (name + '.qasm')
    q.write_text(text)
    (OUT / (name + '.json')).write_text(json.dumps({'data_qubits': data,
        'source': f'PRE2 merge prefix={prefix.name}; L5 A+BC cand_best_m',
        'pre_end': pend, 'round_start': R}, indent=2) + '\n')
    print(name, 'pre_end', pend, 'round', R, 'lines', len(text.splitlines()))


def merge_with_detectors(name, prefix, detectors, compact=False):
    old = dm.PRE_DETECTORS
    dm.PRE_DETECTORS = detectors
    try:
        merge(name, prefix, compact=compact)
    finally:
        dm.PRE_DETECTORS = old


def v14_no_step20():
    lines = v14_prefix(narrow=True).splitlines()
    out = []
    for i, s in enumerate(lines):
        m = re.match(r'measure q\[\d+\] -> c\[(\d+)\];', s)
        if m and int(m.group(1)) < 7:
            continue
        if s in ('h q[1];', 'h q[9];'):
            nxt = next((x for x in lines[i + 1:] if x.strip()), '')
            if nxt.startswith('measure') and re.search(r'c\[[45]\]', nxt):
                continue
        if m and 7 <= int(m.group(1)) <= 13:
            s = re.sub(r'c\[(\d+)\]', lambda z: f'c[{int(z.group(1)) - 7}]', s)
        out.append(s)
    return '\n'.join(out) + '\n'


def measure_init(name):
    src = OUT / (name + '.qasm')
    text = src.read_text()
    text = text.replace('creg c[35];', 'creg c[37];')
    # The L5 BC prep first uses these two helper cells.  A native Z readout
    # preserves the measured |0> value and its record is a detector.
    for q, bit in ((29, 35), (27, 36)):
        old = f'reset q[{q}];'
        pos = text.find(old)
        if pos < 0:
            raise RuntimeError(f'missing first reset q[{q}]')
        text = text[:pos] + f'measure q[{q}] -> c[{bit}];' + text[pos + len(old):]
    text += '// DETECTOR c[35]\n// DETECTOR c[36]\n'
    out = OUT / (name + '_m.qasm')
    out.write_text(text)
    meta = json.loads((OUT / (name + '.json')).read_text())
    meta['source'] += '; first-use q29,q27 measured'
    (OUT / (name + '_m.json')).write_text(json.dumps(meta, indent=2) + '\n')


if __name__ == '__main__':
    variants = {
        'v14_narrow': v14_prefix(narrow=True),
        'v14_nobar': v14_prefix(nobar=True),
        'cp_cultiv_narrow': cp_prefix(),
        'cp_inject_narrow': cp_prefix(('inject',)),
        'compact_nobar': v14_prefix(nobar=True),
        'compact_narrow': v14_prefix(narrow=True),
        'v14_active': v14_prefix(active=True),
        'compact_active': v14_prefix(active=True),
        'no_step20': v14_no_step20(),
        'inject_only': cp_prefix(('inject',)),
    }
    for name, text in variants.items():
        p = write_prefix(name, text)
        try:
            if name == 'no_step20':
                merge_with_detectors(name, p, [f'c[{i}]' for i in range(7)], compact=True)
            elif name == 'inject_only':
                merge_with_detectors(name, p, [f'c[{i}]' for i in range(7)], compact=True)
            else:
                merge(name, p, compact=name.startswith('compact_'))
            if name != 'cp_inject_narrow':
                measure_init(name)
        except Exception as e:
            print(name, 'ERROR', repr(e))
