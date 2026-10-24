import json
import re
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
rows = [r for r in json.loads((HERE / 'exact2.json').read_text())['rows']
        if (HERE / (r['name'] + '.qasm')).exists()]
third = {}
for p in HERE.glob('*.third.log'):
    m = re.search(r'1-F \(to 3rd order\) = ([0-9.eE+-]+)', p.read_text())
    if m:
        third[p.stem.replace('.third', '')] = float(m.group(1))
mc = {}
for p in HERE.glob('*.mc*.log'):
    for line in p.read_text().splitlines():
        if line.startswith('{'):
            try:
                x = json.loads(line)
                mc.setdefault(x['name'], {})[str(x['seed'])] = x
            except Exception:
                pass

def mmean(x):
    vals = [x[str(s)]['score'] for s in (0, 1000, 2000) if str(s) in x]
    return (sum(vals) / len(vals), float(np.std(vals, ddof=1) / np.sqrt(len(vals)))) if len(vals) == 3 else (None, None)

def sitelabel(name):
    try:
        m = json.loads((HERE / (name + '.json')).read_text())
        v, s = m.get('variant'), m.get('sites', [])
        if v == 'first_use_z_reset':
            return 'Z reset ' + (','.join('q' + str(q) for q in s) if s else 'none')
        if v.startswith('fresh_plus'):
            return 'RX→MX ' + ','.join('q' + str(q) for q in s)
        if v == 'retained_x_measurement':
            return 'retain ' + ','.join('q' + str(q) for q in s)
        if v == 'combined':
            return 'combined'
    except Exception:
        pass
    return 'baseline'

out = [
    '# INIT measurement variants', '',
    'Exact values use `work/lanes/EVAL/exact2.py` at p=1e-3. Every emitted QASM passed `tprep.check` at 1e6 shots; see `validation.json`.', '',
    'v12 first-use ordinary Z resets: q2,q9,q14,q16,q20. cand14: q2,q9,q12,q14,q16,q17,q20,q21,q22,q23,q26,q27. The cand14 reset screen keeps every singleton and q16 paired with each other site; the remaining subsets follow the measured additivity pattern.', ''
]
for target in ('v12', 'cand14'):
    out += [f'## {target}', '', '| Variant | Sites | Exact 2nd | Exact 3rd | First order | exp(-A1) |', '|---|---|---:|---:|---:|---:|']
    rr = [r for r in rows if r['name'].startswith(target + '_')]
    for r in rr:
        n, t = r['name'], third.get(r['name'])
        tcol = '—' if t is None else f'{t:.8e}'
        out.append(f"| `{n}` | {sitelabel(n)} | {r['loss2']:.8e} | {tcol} | {r['first']:.2e} | {r['expA']:.6f} |")
    out += ['', 'Finalists (exact third-order ranking):', '', '| Variant | Seed 0 | Seed 1000 | Seed 2000 | 3-seed mean ± SEM |', '|---|---:|---:|---:|---:|']
    wanted = {
        'v12': ['v12_combo_r16_ret8_rx0', 'v12_q16_measure'],
        'cand14': ['cand14_combo_r23_ret8_rx29', 'cand14_combo_r23_ret8_rx0'],
    }[target]
    finalists = [next(r for r in rr if r['name'] == n) for n in wanted]
    for r in finalists:
        n, x = r['name'], mc.get(r['name'], {})
        av, se = mmean(x)
        vals = [x.get(str(s), {}).get('score') for s in (0, 1000, 2000)]
        f = lambda v: '—' if v is None else f'{v:.8e}'
        out.append(f'| `{n}` | {f(vals[0])} | {f(vals[1])} | {f(vals[2])} | {f(av)} ± {f(se)} |')
    out.append('')
out += [
    'RX folds accepted by the noiseless judge: v12 q4,q10,q19; cand14 q4,q5,q10,q11,q25,q28,q29. Other fresh RX sites were rejected after exact detector folding because the output was no longer in the code space.',
    'The cand14 q29 finalist has all three 1e8-shot seeds. The near-tied q29-free combined candidate is fully judge-validated at 1e6 and has exact third-order data; its 1e8-shot run was stopped after the q29 finalist completed because the cand14 sampler exceeded the available run window.',
    ''
]
(HERE / 'REPORT.md').write_text('\n'.join(out))
