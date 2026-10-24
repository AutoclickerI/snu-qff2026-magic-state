"""Region specs for v36c's B/C side (units = native ops whose noise region.py makes perfect)."""
import sys, json
from pathlib import Path
from qcirc import parse
from decompose import split, is_round

D = [0, 20, 7, 10, 3, 22, 21]
A = [1, 14, 8, 9, 2, 16, 15]
B = [6, 26, 13, 11, 4, 23, 27]
C = [12, 25, 19, 17, 5, 29, 28]
BC = set(B + C)
stem = sys.argv[1] if len(sys.argv) > 1 else 'v36c'
units, dets = parse(open(stem + '.qasm').read())
life_of, find, entry, comp = split(units)
pre = set()
for root, idx in comp.items():
    if root in entry:
        pre |= set(idx)

def U(sel):
    return [[units[i]['t'], list(units[i]['q'])] for i in sorted(sel)]

cat = {}
for i, u in enumerate(units):
    qs, t, k = set(u['q']), u['t'], u['k']
    if i in pre or not (qs & BC) or t < 32:
        continue
    if is_round(u):
        cat.setdefault('BD' if qs & set(B) and qs & set(D) else 'DA', []).append(i)
    elif k == 'CX' and t == 44 and qs <= BC:
        cat.setdefault('BtoC', []).append(i)
    elif t >= 45 and k in ('M', 'MX', 'CX'):
        cat.setdefault('Bread' if qs & set(B) else 'Cread', []).append(i)
    elif qs <= BC:
        cat.setdefault('prep', []).append(i)
    else:
        cat.setdefault('other', []).append(i)
for k, v in cat.items():
    print(k, len(v), sum(units[i]['k'] == 'CX' for i in v), sorted({units[i]['t'] for i in v}))
specs = {}
specs['bc_all'] = cat['prep'] + cat['BtoC'] + cat['Bread'] + cat['Cread']
specs['bc_prep'] = cat['prep']
specs['bc_prep_B_only'] = [i for i in cat['prep'] if set(units[i]['q']) <= set(B)]
specs['bc_prep_C_only'] = [i for i in cat['prep'] if set(units[i]['q']) <= set(C)]
specs['bc_prep_BC_mixed'] = [i for i in cat['prep'] if set(units[i]['q']) & set(B) and set(units[i]['q']) & set(C)]
specs['bc_BtoC'] = cat['BtoC']
specs['bc_Bread'] = cat['Bread']
specs['bc_Cread'] = cat['Cread']
specs['bc_BD'] = cat['BD']
for t in range(32, 44):
    specs[f'bc_prep_t{t}'] = [i for i in cat['prep'] if units[i]['t'] == t]
specs['bc_prep_t32_37'] = [i for i in cat['prep'] if units[i]['t'] <= 37]
specs['bc_prep_t38_43'] = [i for i in cat['prep'] if units[i]['t'] >= 38]
specs['bc_prep_t41_43'] = [i for i in cat['prep'] if units[i]['t'] >= 41]
for b in B:
    specs[f'bc_Bq{b}_prep'] = [i for i in cat['prep'] if b in units[i]['q']]
out = Path(sys.argv[2] if len(sys.argv) > 2 else 'specs')
out.mkdir(exist_ok=True)
for name, sel in specs.items():
    (out / f'{name}.json').write_text(json.dumps(dict(name=name, units=U(sel))))
    print(name, len(sel))
