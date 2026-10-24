"""Archive exact hashes/recipes before removing regenerable experiment bulk."""
from mbp import *
import hashlib,csv,copy
original=prefix;cache={}
def cached(which):
    if which not in cache:cache[which]=original(which)
    return copy.deepcopy(cache[which])
import mbp
mbp.prefix=cached
rows=[]
for f in sorted(OUT.rglob('*.result.json')):
    r=json.loads(f.read_text());qf=f.with_name(f.name.replace('.result.json','.qasm'))
    if not r.get('grid_free') or not qf.exists():continue
    nq=r['n_qubits'];relax(nq)
    text,_=build(r['blocks'],r['kind'],r['R'],r['order'],r['perm'],r['pre'],nq==64,r.get('red_mask',7))
    if nq==72:
        assert r['blocks']=='A';text=text.replace('qreg q[84];','qreg q[72];')
    old=qf.read_text();assert text==old,(f,'regeneration mismatch')
    rows.append(dict(name=str(f.relative_to(OUT)).removesuffix('.result.json'),sha256=hashlib.sha256(old.encode()).hexdigest(),pre=r['pre'],R=r['R'],blocks=r['blocks'],kind=r['kind'],order=''.join(map(str,r['order'])),perm=''.join(map(str,r['perm'])),n_qubits=nq,red_mask=r.get('red_mask',7),legacy_single=nq==64))
with (OUT/'recipes.csv').open('w') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
(OUT/'regeneration.receipt.json').write_text(json.dumps(dict(verified=len(rows),status='all QASM reproduced byte-for-byte from retained inputs and recipe fields'),indent=2)+'\n')
print('byte-for-byte regenerated',len(rows),'grid-free circuits',flush=True)
