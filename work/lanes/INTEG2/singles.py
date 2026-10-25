"""Single-gadget and acceptance-trade menu on a base plan (INTEG echoes/pairs, PRECELL guards, INTEG p1 trades),
legality re-derived on the base's own schedule.
usage: singles.py <base under c/> -> c/<base>__S_<name>, list in singles_<base>.list, specs in singles_<base>.json"""
from gadgets import *
import gadgets as G
import guards_pc as GP

base = sys.argv[1] if len(sys.argv) > 1 else 'i2_v36f'
c = read(C / base)
st = status(c)
names, specs = [], {}


def emit(cc, key, spec):
    n = f'{base}__S_{key}'
    if n in specs:
        return
    try:
        save(cc, n, dict(kind='single', base=base, spec=spec))
        names.append(n); specs[n] = spec
    except Exception as e:
        print('fail', key, repr(e)[:160])


# INTEG echoes: maximal windows per (q, h, axis)
by = collections.defaultdict(list)
for e in echoes(c, st):
    by[(e['q'], e['h'], e['axis'])].append(e)
for v in by.values():
    for e in v:
        if not any(f is not e and f['t1'] <= e['t1'] and f['t2'] >= e['t2'] for f in v):
            emit(add_echo(c, e), G.gname(e) + ('r' if e.get('rst') is not None else ''), dict(family='echo', g=e))
# INTEG pairs: one per idle run with constant status, data-data excluded
runs = collections.defaultdict(list)
for p in pairs(c, st):
    if p['a'] in D and p['b'] in D:
        continue
    runs[(p['a'], p['b'])].append(p)
for v in runs.values():
    v.sort(key=lambda p: p['t'])
    groups = [[v[0]]]
    for p in v[1:]:
        if p['t'] == groups[-1][-1]['t'] + 1 and p['sa'] == groups[-1][-1]['sa'] and p['sb'] == groups[-1][-1]['sb']:
            groups[-1].append(p)
        else:
            groups.append([p])
    for g in groups:
        p = g[len(g) // 2]
        emit(add_pair(c, p), G.gname(p), dict(family='pair', g=p, run=[q['t'] for q in g]))
# PRECELL guards
for g in GP.menu(c):
    emit(GP.apply(c, g), GP.gname(g), dict(family='guard', g=g))
# acceptance trades: prep delays and single checks
for r in prep_options(c):
    emit(delay_preps(c, [r]), f"pd_q{r['q']}_{r['old']}_{r['new']}", dict(family='trade', kind='prep_delay', edit=r))
S1 = sorted({int(BITRE.findall(l)[0]) for l in c['tail'] if l.startswith('// DETECTOR') and len(BITRE.findall(l)) == 1})
for b in S1:
    for mode in ('detector', 'omit', 'reset'):
        try:
            cc = remove_check(c, b, mode)
        except Exception:
            continue
        emit(cc, f'{mode}_{b}', dict(family='trade', kind='check', bit=b, mode=mode))
(H / f'singles_{base}.list').write_text(' '.join(names))
(H / f'singles_{base}.json').write_text(json.dumps(specs))
print(len(names), collections.Counter(s['family'] for s in specs.values()))
