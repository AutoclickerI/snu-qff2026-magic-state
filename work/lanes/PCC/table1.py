"""Stage-1 table from s1/res_batch1.jsonl (+ s1/res_batch2.jsonl if present)."""
import json, sys
from pathlib import Path
REF, REFA = 3.815473322405639e-05, 0.5016415049479503
D = Path(__file__).with_name('s1')
rows = {}
for f in ('res_batch1.jsonl', 'res_batch2.jsonl'):
    p = D / f
    if p.exists():
        for l in p.read_text().splitlines():
            r = json.loads(l); rows[r['spec']] = r
A0 = rows['k0:a']
def sup(name):
    return json.loads((D / (name + '.json')).read_text())['support']
print(f"A0 (k0, ideal C readout): {A0['loss']:.10e} acc {A0['acceptance']:.5f}  vs v36h {A0['loss']-REF:+.3e}")
hdr = 'V basis   | k | supp      | (a) loss     acc     d vs A0   | (b) loss     acc     d v36h    | (c) d v36h  acc     | strip d v36h | (b)-strip | (bi) d v36h'
print(hdr)
out = []
for name in sorted({k.split(':')[0] for k in rows if k.startswith('v')}, key=lambda n: (n.count('_'), n)):
    a, b, c = rows.get(name + ':a'), rows.get(name + ':b'), rows.get(name + ':c')
    s = sup(name)
    sn = 'strip' + ''.join(map(str, s)) + ':s'
    st, bi = rows.get(sn), rows.get(name + ':bi')
    k = name.count('_') + 1
    line = (f"{name[1:]:9} | {k} | {''.join(map(str, s)):9} | {a['loss']:.6e} {a['acceptance']:.5f} {a['loss']-A0['loss']:+.3e} | "
            f"{b['loss']:.6e} {b['acceptance']:.5f} {b['loss']-REF:+.3e} | {c['loss']-REF:+.3e} {c['acceptance']:.5f} | "
            + (f"{st['loss']-REF:+.3e}   | {b['loss']-st['loss']:+.3e} | " if st else '  -          |   -        | ')
            + (f"{bi['loss']-REF:+.3e}" if bi else '-'))
    print(line)
    out.append(dict(V=name[1:], k=k, support=s, a=a, b=b, c=c, strip=st, bi=bi))
(D / 'table1.json').write_text(json.dumps(dict(ref=REF, A0=A0, rows=out), indent=1))
