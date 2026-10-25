"""Port BUNDLE's v36h triples onto v36k: price (v36k's edit set S) + each v36h-positive triple, on base v36i.
argv: S json file, triples jsonl, top N, processes, out jsonl."""
import sys, json
from multiprocessing import get_context
from pathlib import Path
H = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(H))
import menu as M, ev as E
BASE = M.read(H.parents[0] / 'MAIN' / 'v36i')
EDITS = json.load(open(H / 'res' / 'menu.json'))
tau_h = 3.815473322483099e-05
S = json.load(open(sys.argv[1]))
rows = sorted([r for r in map(json.loads, open(sys.argv[2])) if r.get('loss') and r['loss'] < tau_h], key=lambda r: r['loss'])
seen, cands = set(), []
for r in rows:
    b = tuple(sorted(set(S) | set(r['b'])))
    if b not in seen and not set(r['b']) <= set(S):
        seen.add(b); cands.append((r['b'], b))
    if len(cands) >= int(sys.argv[3]):
        break
def price(c):
    t, b = c
    try:
        _, txt = M.apply_bundle(BASE, [EDITS[i] for i in b])
    except M.Invalid:
        return dict(t=t, invalid=True)
    r = E.price_stem(E.write_stem(txt))
    return dict(t=t, **{k: r[k] for k in ('loss', 'acceptance') if k in r})
with get_context('fork').Pool(int(sys.argv[4])) as pool, open(sys.argv[5], 'a') as out:
    out.write(json.dumps(dict(base=price(((), tuple(S))))) + '\n')
    for r in pool.imap_unordered(price, cands):
        out.write(json.dumps(r) + '\n'); out.flush()
