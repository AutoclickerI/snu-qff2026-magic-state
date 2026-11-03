"""First-W GHZ growth flag using native boundary helper q13.

The helper is measured before its terminal-resource reset, so this uses the
existing clock and imposes no wait on that resource. Later cat is fully decoded.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json
from pathlib import Path
from late_cat import ROOT,HERE,A,D,emit,Circuit
from qtools import write_stem,price
from qtools.validity import raw_check
from qtools.evaluator.frontend import parse_current

def build(stem):
    stem=Path(stem);meta=json.loads(stem.with_suffix('.json').read_text())['source']
    ops,dets=parse_current(stem.with_suffix('.qasm').read_text())
    assert meta['checks']==2 and meta['uncompute']=='full' and meta['reuse']
    t=meta['cat_start'];removed=[o for o in ops if t<=o.time<=t+8 and set(o.qs)&set(A)]
    rids={id(o) for o in removed};rbits={o.bit for o in removed if o.bit is not None}
    assert not any(13 in o.qs and o.time<=t+6 for o in ops)
    c=Circuit();c.bit=max(o.bit for o in ops if o.bit is not None)+1
    c.dets=[sorted(row) for row in dets if not row&rbits]
    for o in ops:
        if id(o) not in rids:emit(c,o.time,o)
    for q in A:c.reset(t,q,q==14)
    c.reset(t,13);c.cx(t+1,14,13)
    tree=[[(14,8)],[(14,15),(8,2)],[(15,16),(8,9),(2,1)]]
    for j,layer in enumerate(tree,2):
        for u,v in layer:c.cx(t+j,u,v)
    c.cx(t+5,14,13)
    for a,d in zip(A,D):c.cx(t+6 if a==14 else t+5,a,d)
    c.dets.append([c.read(t+6,13)])
    c.dets.append([c.read(t+7 if a==14 else t+6,a,True) for a in A])
    for q in A:c.reset(t+8,q,q==8)
    nops,nds=parse_current(c.text());used=set()
    for o in nops:
        keys={(o.time,q) for q in o.qs};assert not used&keys,(o,used&keys);used|=keys
        if o.kind=='CX':assert abs(o.qs[0]//6-o.qs[1]//6)+abs(o.qs[0]%6-o.qs[1]%6)==1
    out=dict(meta);out.update(source_stem=str(stem),growth_flag_helper=13,
        cx=sum(o.kind=='CX' for o in nops),ticks=max(o.time for o in nops)+1)
    return c,out

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--price',action='store_true');a=ap.parse_args()
    c,meta=build(a.stem);stem=write_stem(c.text(),D,HERE/'cand','growth_flag13',source=meta)
    r=dict(stem=str(stem),**meta,raw=raw_check(c.text(),D));print(json.dumps(r,indent=2),flush=True)
    if a.price and r['raw']['ok']:r['price']=price(stem,processes=1);print(json.dumps(r['price'],indent=2),flush=True)
    stem.with_suffix('.result.json').write_text(json.dumps(r,indent=2)+'\n')
