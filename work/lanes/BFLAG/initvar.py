"""R-then-M init variants on a base: for listed cells, the init R@t becomes R@t-1 + M@t (literal of the reset;
X_ERROR before measure + DEPOL1 after leaves 2p/3 harmful X instead of the reset's p, plus one detector).
usage: initvar.py <syn.json> <name> <base> <q,q,...>"""
import sys, json
from pathlib import Path
import mkcand, splice, proxy

sol = json.load(open(sys.argv[1])); name, base = sys.argv[2], sys.argv[3]
cells = [int(q) for q in sys.argv[4].split(',')]
here = Path(__file__).parent
spec = mkcand.spec_from(sol, 'default', mkcand.BASE_NONFRESH[base])
for q in cells:
    k, t = spec['inits'][str(q)]
    assert k == 'R', (q, k)
    spec['inits'][str(q)] = ['M', t]
    spec['extra'].append([t - 1, 'R', q])
bu, bd = splice.load(here / base)
old = None
if base != 'v36c':
    also, absent = mkcand.BASE_ALSO[base]
    old = splice.prep_by_keys(bu, splice.load(here / 'v36c')[0], also, absent)
u, d, nb = splice.build(bu, bd, spec, old=old)
splice.write(here / 'cand' / name, u, d, nb, dict(source='BFLAG initvar', syn=sys.argv[1], rm=cells, base=base))
flags = sorted({e[2] for e in spec['extra'] if e[2] not in mkcand.CELLS})
s, _, _ = proxy.analyse(u, d, flags=flags, starts=mkcand.starts_of(spec))
print(name, json.dumps(s))
