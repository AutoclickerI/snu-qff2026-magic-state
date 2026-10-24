"""Joint fill on BASE: priced singles plus unpriced pair ticks inferred from a priced tick in the same idle run.

p4_fill.py BASE TAG [acc_floor_estimate]
Greedy by gain; echoes and other acceptance-costing gadgets are taken while estimated acceptance stays above
the floor estimate. Writes prefix circuits after each block of 4 additions and the final one.
"""
from joint import *
import glob

base, tag = sys.argv[1], sys.argv[2]
afloor = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5035
c0 = load_plan(base)
st0 = status(c0)
bl = {b: json.loads((H / 'res' / (b + '.json')).read_text()) for b in ('F5', 'F6', 'F6__J4a')}
priced = {}
for f in glob.glob(str(H / 'res' / 'F[56]__*.json')):
    if '__J4a__' not in f and '__J' in f:
        continue
    if '.acc.' in f or 'adj' in f:
        continue
    r = json.loads(open(f).read())
    n = r.get('name', '')
    if 'loss' not in r or 'late' in n or 'star' in n:
        continue
    g = json.loads((C / n).with_suffix('.json').read_text())['integ'].get('gadget')
    if not g:
        continue
    b = bl[n.rsplit('__', 1)[0]]
    priced[gname(g) + ('r' if g.get('rst') is not None else '')] = dict(n=n, g=g, gain=b['loss'] - r['loss'], cost=b['acceptance'] - r['acceptance'])


def runs_of(a, b, st):
    """contiguous tick runs where both are idle with constant status."""
    T = len(st[a])
    out, cur = [], []
    for t in range(T):
        ok = st[a][t] in ('live', 'dead', 'prem') and st[b][t] in ('live', 'dead', 'prem')
        key = (st[a][t], st[b][t])
        if ok and cur and cur[-1][1] == key and cur[-1][0] == t - 1:
            cur.append((t, key))
        else:
            if cur:
                out.append(cur)
            cur = [(t, key)] if ok else []
    if cur:
        out.append(cur)
    return [[t for t, _ in r] for r in out]


items = {k: v for k, v in priced.items()}
# infer unpriced pair ticks
for p in pairs(c0, st0):
    k = gname(p)
    if k in items or (p['a'] in D and p['b'] in D):
        continue
    for run in runs_of(p['a'], p['b'], st0):
        if p['t'] in run and p['t'] + 1 in run:
            ref = [items[f"pair_{p['a']}_{p['b']}_{t}"] for t in run if f"pair_{p['a']}_{p['b']}_{t}" in items and items[f"pair_{p['a']}_{p['b']}_{t}"].get('inferred') is None]
            if ref:
                items[k] = dict(n=None, g=p, gain=ref[0]['gain'], cost=ref[0]['cost'], inferred=ref[0]['n'])
rows = [v for v in items.values() if v['gain'] > float(os.environ.get('MINGAIN', '5e-10'))]
rows.sort(key=lambda r: ((r['g']['kind'] != 'echo') if os.environ.get('ECHOFIRST') else 0, -r['gain']))
Lb = json.loads((H / 'res' / (base + '.json')).read_text())
acc = Lb['acceptance']
c = c0
used = []
moves = [dict(kind='move', q=q, t0=t0, t1=t1) for q, t0, t1 in json.loads(os.environ.get('MOVES', '[]'))]
for m in moves:
    c = apply(c, m)
    used.append(dict(g=m, gain=0, cost=0))
for _pass in range(2):
    for r in rows:
        if any(u is r for u in used):
            continue
        if r['cost'] > 0 and acc - r['cost'] < afloor:
            continue
        if not valid(c, r['g']):
            continue
        c2 = apply(c, r['g'])
        try:
            normalized(c2)
        except Exception:
            continue
        c = c2
        used.append(r)
        acc -= r['cost']
print(len(rows), 'candidates', len(used), 'used', 'est_gain', sum(u['gain'] for u in used), 'est_acc', acc)
n = f'{base}__{tag}'
save(c, n, dict(kind='joint', base=base, gadgets=[u['g'] for u in used], est_gain=sum(u['gain'] for u in used), est_acc=acc,
                inferred=[gname(u['g']) for u in used if u.get('inferred')]))
print(n, 'inferred', sum(1 for u in used if u.get('inferred')))
for u in used:
    print(f"  {gname(u['g'])}{'r' if u['g'].get('rst') is not None else ''} gain={u['gain']:.2e} cost={u['cost']:+.5f}{' (inferred)' if u.get('inferred') else ''}")
