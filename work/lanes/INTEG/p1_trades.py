"""Phase 1: acceptance-only trades on v36c (prep delays, single-check removals)."""
from lib import *

c = read(C / 'v36c')
rows = []


def emit(cc, name, desc):
    try:
        save(cc, name, desc)
        rows.append(dict(name=name, desc=desc))
    except Exception as e:
        rows.append(dict(name=name, desc=desc, error=repr(e)))
        print(name, repr(e)[:200], flush=True)


opts = prep_options(c)
for r in opts:
    emit(delay_preps(c, [r]), f'pd_q{r["q"]}', dict(kind='prep_delay', edit=r))
emit(delay_preps(c, opts), 'pd_all', dict(kind='prep_delay', edits=opts))
singles = sorted({int(BITRE.findall(l)[0]) for l in c['tail'] if len(BITRE.findall(l)) == 1})
for b in singles:
    for mode in ('detector', 'omit', 'reset'):
        try:
            cc = remove_check(c, b, mode)
        except Exception as e:
            continue
        emit(cc, f'{mode}_{b}', dict(kind='check', bit=b, mode=mode))
(H / 'p1_rows.json').write_text(json.dumps(rows, indent=1))
print(len(rows), 'built', sum('error' in r for r in rows), 'errors')
