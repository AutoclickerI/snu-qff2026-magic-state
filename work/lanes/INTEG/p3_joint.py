"""Joint proposals: rank priced singles by gain per acceptance, compose prefixes onto a base.

p3_joint.py BASE TAG FLOOR name1 name2 ...   (names are priced singles 'X__gadget' on any base)
Writes c/BASE__TAG_k for k = 1..n (prefix of the ranked list, conflicts skipped) and prints names.
"""
from joint import *

base, tag, floor = sys.argv[1], sys.argv[2], float(sys.argv[3])
mode = 'rate'
if sys.argv[4] in ('gain', 'rate'):
    mode = sys.argv.pop(4)
singles = sys.argv[4:]
c0 = load_plan(base)


def price(n):
    r = json.loads((H / 'res' / (n + '.json')).read_text())
    return r['loss'], r['acceptance']


rows = []
for n in singles:
    sb = n.split('__')[0]
    Lb, Ab = price(sb)
    L, A = price(n)
    g = json.loads((C / n).with_suffix('.json').read_text())['integ']['gadget']
    gain, cost = Lb - L, Ab - A
    if gain <= 0:
        continue
    rows.append(dict(n=n, g=g, gain=gain, cost=cost, rate=gain / max(cost, 1e-7)))
rows.sort(key=lambda r: -r[mode])
Lb, Ab = price(base)
out = []
c = c0
used = []
acc_est = Ab
for r in rows:
    if not valid(c, r['g']):
        continue
    c2 = apply(c, r['g'])
    try:
        normalized(c2)
    except Exception:
        continue
    c = c2
    used.append(r)
    acc_est -= r['cost']
    n = f'{base}__{tag}_{len(used)}'
    save(c, n, dict(kind='joint', base=base, gadgets=[u['g'] for u in used], est_gain=sum(u['gain'] for u in used),
                    est_acc=acc_est))
    out.append(n)
    print(n, r['n'], f"rate={r['rate']:.2e} est_gain={sum(u['gain'] for u in used):.3e} est_acc={acc_est:.5f}", flush=True)
    if acc_est < floor - 0.004:
        break
(H / f'p3_{tag}.txt').write_text(' '.join(out))
