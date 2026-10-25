"""Apply slot specs from saved candidates (their json 'integ' desc) onto a base plan.
usage: jslot.py <base stem> <out> <cand name> ..."""
import sys, json
from elements import *
base, out = sys.argv[1], sys.argv[2]
c = read(base)
applied = []
for n in sys.argv[3:]:
    d = json.loads((C / (n + '.json')).read_text())['integ']
    if 'slot' in d:
        s = d['slot']; h, q, t, kind = s['h'], s['q'], s['t'], s['kind']
        if s['move']:
            t_old, t_new, lines = s['move']
            o = next(o for o in c['ops'] if o['t'] == t_old and o['lines'] == lines)
            o['t'] = t_new
    elif 'kslot' in d:
        s = d['kslot']; h, q, t, kind = s['h'], s['q'], s['t'], s['P']
    else:
        raise ValueError(d)
    line = f'cx q[{h}],q[{q}];' if kind == 'Z' else f'cx q[{q}],q[{h}];'
    c = add_ops(c, [(t, [line])])
    applied.append(n)
print(save(c, out, desc=dict(base=base, slots=applied)))
