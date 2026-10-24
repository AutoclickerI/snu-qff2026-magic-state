"""Tick-by-tick dump of a barrier-synchronised circuit: per-qubit timeline and per-tick op list."""
import sys, re, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'MAIN' / 'sparse'))
from frontend import parse_current
stem = Path(sys.argv[1])
text = stem.with_suffix('.qasm').read_text()
ops, dets = parse_current(text)
T = max(o.time for o in ops) + 1
used = sorted({q for o in ops for q in o.qs})
sym = {}
cell = {q: ['.'] * T for q in used}
for o in ops:
    k = o.kind
    if k == 'CX':
        c, t = o.qs
        cell[c][o.time] = f'C{t}'
        cell[t][o.time] = f'T{c}'
    else:
        for q in o.qs:
            s = {'R': 'R', 'RX': 'RX', 'M': f'M{o.bit}', 'MX': f'MX{o.bit}', 'T': 't', 'TDG': 'td', 'H': 'h'}.get(k, k)
            cell[q][o.time] = s
w = 6
print('tick ' + ''.join(f'{t:<{w}}' for t in range(T)))
for q in used:
    print(f'q{q:<3} ' + ''.join(f'{s:<{w}}'[:w] for s in cell[q]))
