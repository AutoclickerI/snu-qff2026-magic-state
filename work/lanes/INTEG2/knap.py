"""Knapsack joint from priced singles on MENU_BASE: gadgets by gain (validity re-checked as composed), then acceptance trades
cheapest per unit acceptance until the additive acceptance estimate reaches FLOOR + MARGIN. Writes prefix circuits
c/<tag>_k<n> after every gadget and the final c/<tag>_final, priced whole in parallel.
usage: knap.py <tag> [floor=0.5010] [margin=0.0008] [mingain=1e-11] [exclude regex]"""
import re as _re
from greedy import *

tag = sys.argv[1]
floor = float(sys.argv[2]) if len(sys.argv) > 2 else 0.5010
margin = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0008
mg = float(sys.argv[4]) if len(sys.argv) > 4 else 1e-11
excl = _re.compile(sys.argv[5]) if len(sys.argv) > 5 else None
rows = menu()
b0 = price(MB)
gad = sorted([r for r in rows if r['spec']['family'] in ('echo', 'pair', 'guard') and r['gain'] > mg
              and not (excl and excl.search(r['n']))], key=lambda r: -r['gain'])
trd = [r for r in rows if r['spec']['family'] == 'trade' and r['dacc'] > 1e-4]
trd.sort(key=lambda r: max(-r['gain'], 0) / r['dacc'])
c = load_plan(MB) if (C / (MB + '.plan.json')).exists() else read(C / MB)
used, names, acc = [], [], b0['acceptance']
for r in gad:
    try:
        c2 = apply_spec(c, r['spec'])
    except Invalid:
        continue
    c = c2; used.append(r); acc += r['dacc']
    names.append(save_joint(c, f'{tag}_k{len(used)}', MB, [u['spec'] for u in used]))
    print(f"+ {r['n'].split('__', 1)[1]} {-r['gain']:+.2e} {r['dacc']:+.5f} est_acc {acc:.5f}")
for r in trd:
    if acc >= floor + margin:
        break
    try:
        c2 = apply_spec(c, r['spec'])
    except Invalid:
        continue
    c = c2; used.append(r); acc += r['dacc']
    print(f"+ trade {r['n'].split('__', 1)[1]} {-r['gain']:+.2e} {r['dacc']:+.5f} est_acc {acc:.5f}")
names.append(save_joint(c, f'{tag}_final', MB, [u['spec'] for u in used]))
res = run_prices(names)
for n in names:
    r = res[n]
    print(f"{n} loss {r['loss']!r} ({r['loss'] - b0['loss']:+.4e}) acc {r['acceptance']:.5f}" if r else f'{n} ERROR')
