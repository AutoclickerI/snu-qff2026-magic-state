"""Timing moves: shift one unit (gate, init, measurement) to another tick with per-qubit order kept (the noiseless
circuit is unchanged; only idle placement moves). usage: shift.py <base> <tag> [maxd=2] [tmin=0]
-> c/<tag>_<t>_<qubits>_<newt>, list in <tag>.list, specs in <tag>.json (family 'loo' edits: move)."""
from elements import *

base, tag = sys.argv[1], sys.argv[2]
maxd = int(sys.argv[3]) if len(sys.argv) > 3 else 2
tmin = int(sys.argv[4]) if len(sys.argv) > 4 else 0
c = load_plan(base) if (C / (base + '.plan.json')).exists() else read(C / base)
T = depth(c)
occ = busy(c)
names, specs = [], {}
for o in c['ops']:
    u = unit(o)
    if o['t'] < tmin:
        continue
    qs = u.qs
    lo, hi = -1, T
    for q in qs:
        s = seq(c, q)
        k = next(i for i, x in enumerate(s) if x is o)
        if k > 0:
            lo = max(lo, s[k - 1]['t'])
        if k + 1 < len(s):
            hi = min(hi, s[k + 1]['t'])
    for nt in range(o['t'] - maxd, o['t'] + maxd + 1):
        if nt == o['t'] or nt <= lo or nt >= hi or nt < 0 or nt >= T:
            continue
        if any(q in occ[nt] for q in qs):
            continue
        key = (o['t'], tuple(qs), u.name)
        if u.name == 'CX':
            ed = [('move', o['t'], tuple(cx_qs(o)), 'CX', nt)]
        else:
            ed = [('move', o['t'], qs[0], u.name, nt)]
        n = f"{tag}_{o['t']}_{u.name}_{'_'.join(map(str, qs))}_{nt}"
        try:
            save(strip(c, ed), n, dict(kind='shift', base=base))
        except Exception as e:
            continue
        names.append(n); specs[n] = dict(family='loo', element=n, edits=ed)
(H / f'{tag}.list').write_text(' '.join(names))
(H / f'{tag}.json').write_text(json.dumps(specs))
print(len(names))
