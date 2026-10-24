import json,sys
from pathlib import Path
H=Path(__file__).resolve().parent
def price(n):
    r=json.loads((H/'res'/(n+'.json')).read_text()); return r.get('loss'),r.get('acceptance')
rs=[json.loads(l) for f in sys.argv[1:] for l in open(f) if l.startswith('{')]
out=[]
for r in rs:
    if 'loss' not in r: print('ERR',r['name'],r.get('error','')[:150]); continue
    b=r['name'].split('__')[0]; L0,A0=price(b)
    out.append((r['loss']-L0,r,L0,A0))
out.sort(key=lambda x:x[0])
for d,r,L0,A0 in out:
    print(f"{r['name']:34s} L={r['loss']:.6e} dL={d:+.3e} ({d/L0*100:+.3f}%) A={r['acceptance']:.5f} dA={r['acceptance']-A0:+.5f} rate={-d/max(1e-7,A0-r['acceptance']):.2e}")
print(len(out))
