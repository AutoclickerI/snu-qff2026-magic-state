import json,sys,glob
from pathlib import Path
H=Path(__file__).resolve().parent
base={}
for b in ('F5','F6'):
    base[b]=json.loads((H/'res'/(b+'.json')).read_text())['loss']
out=[]
for f in glob.glob(str(H/'res'/'F[56]__*.json')):
    if '.acc.' in f or '__J' in f or 'adj' in f: continue
    r=json.loads(open(f).read())
    if 'loss' not in r: continue
    n=r['name']; b=n.split('__')[0]
    if 'late' in n or 'star' in n: continue
    if r['loss']<base[b]-float(sys.argv[1] if len(sys.argv)>1 else 5e-10): out.append(n)
print(' '.join(out))
