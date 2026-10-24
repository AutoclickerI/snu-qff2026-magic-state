"""Per-cell init kind choice (R vs M for |0> cells, MX vs RX for fresh pivots) by the proxy J, coordinate descent.
usage: initopt.py <syn.json> [KZ KA]"""
import sys, json, itertools
import mkcand, splice, proxy, lns
from pathlib import Path
KZ = float(sys.argv[2]) if len(sys.argv) > 2 else 8e-5
KA = float(sys.argv[3]) if len(sys.argv) > 3 else 2.6e-5
sol = json.load(open(sys.argv[1]))
if 'T0' not in sol: sol['T0'] = 33
base_policy = sol.get('policy', 'default')
spec0 = mkcand.spec_from(sol, base_policy)
choices = {}
piv = set(int(q) for q in sol['pivots'])
for q, (k, t) in spec0['inits'].items():
    qi = int(q)
    if qi in piv:
        choices[q] = ['MX', 'RX'] if qi in mkcand.FRESH else [k]
    else:
        opts = ['R']
        if qi in mkcand.FRESH or qi in mkcand.LITERAL0:
            opts.append('M')
        if qi in mkcand.LITERAL0:
            opts.append('none')
        choices[q] = opts
def J(pol):
    spec = mkcand.spec_from(sol, pol)
    u, d, nb = splice.build(lns.BASE[0], lns.BASE[1], spec)
    s, _, _ = proxy.analyse(u, d, flags=sorted({e[2] for e in spec['extra'] if e[2] not in mkcand.CELLS}), starts=mkcand.starts_of(spec))
    if s['c1'] > 1e-12: return None, s
    return s['X2'] + KZ * s['RZ'] + KA * s['acc1'], s
pol = {q: k for q, (k, t) in spec0['inits'].items()}
cur, s = J(pol)
print('start', cur, s)
improved = True
while improved:
    improved = False
    for q, opts in choices.items():
        for k in opts:
            if k == pol.get(q): continue
            p2 = dict(pol); p2[q] = k
            try:
                j, s2 = J(p2)
            except AssertionError:
                continue
            if j is not None and j < cur - 1e-13:
                cur, pol, s = j, p2, s2; improved = True
                print('set', q, k, cur, json.dumps({kk: s[kk] for kk in ('X2', 'RZ', 'acc1')}))
print('final', cur, json.dumps(pol))
json.dump(dict(sol, policy=pol), open(sys.argv[1].replace('.json', '_init.json'), 'w'))
