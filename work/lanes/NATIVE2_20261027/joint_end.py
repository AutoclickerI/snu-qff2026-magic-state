"""Integrate END2's independently synthesized B=|0L>, C=0 resource."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import argparse,json
from pathlib import Path
from late_cat import ROOT,HERE,A,D,emit,Circuit
from qtools import write_stem,price
from qtools.validity import raw_check
from qtools.evaluator.frontend import parse_current

def integrate(stem,module_path=None):
    stem=Path(stem)
    module_path=Path(module_path) if module_path else ROOT/'work/lanes/END2_20261027/sol/fresh_native_d13.json'
    module=json.loads(module_path.read_text())['module']
    oldmeta=json.loads(stem.with_suffix('.json').read_text())['source'];R=oldmeta['round_tick']
    ops,dets=parse_current(stem.with_suffix('.qasm').read_text())
    B=module['B'];C=module['C'];resource=set(B+C+[18,31,35,34])
    removed=[o for o in ops if set(o.qs)&resource]
    rbits={o.bit for o in removed if o.bit is not None}
    assert not (set(A+D)&resource)
    c=Circuit();c.bit=max(o.bit for o in ops if o.bit is not None)+1
    original_a=[{14,15,17,18,20},{24,17,19,20},{15,18,19,20,24}]
    for row in dets:
        if row in original_a:c.dets.append(sorted(row-{24}))
        elif not row&rbits:c.dets.append(sorted(row))
    for o in ops:
        if not set(o.qs)&resource:emit(c,o.time,o)
    shift=R-module['last_layer_time'];local={}
    assert shift>=0
    for init in module['initializations']:
        t=shift+init['time'];q=init['q'];x=init['kind']=='MX'
        local[init['bit']]=c.read(t,q,x)
        if x:c.add(t,f'h q[{q}];')
    for row in module['initial_zero_detectors']:c.dets.append([local[b] for b in row])
    for j,layer in enumerate(module['layers']):
        for u,v in layer:c.cx(shift+j,u,v)
    for b,d in zip(B,D):c.cx(R+1,b,d)
    cbits=[c.read(R+1,q) for q in C]
    cchecks=module['C_Z_checks']
    if isinstance(cchecks,str):cchecks=[[i] for i in range(7)]
    for row in cchecks:
        indices=row['C_indices'] if isinstance(row,dict) else row
        c.dets.append([cbits[i] for i in indices])
    bbits=[c.read(R+2,q,True) for q in B]
    for check in module['B_X_checks']:
        c.dets.append([bbits[i] for i in check['B_indices']]+[local[b] for b in check['initial_record_xor']])
    nops,nds=parse_current(c.text());used=set()
    for o in nops:
        keys={(o.time,q) for q in o.qs};assert not used&keys,(o,used&keys);used|=keys
        if o.kind=='CX':assert abs(o.qs[0]//6-o.qs[1]//6)+abs(o.qs[0]%6-o.qs[1]%6)==1
    bits={o.bit for o in nops if o.bit is not None};assert all(row<=bits for row in nds)
    meta=dict(**oldmeta);meta.update(source_stem=str(stem),resource_module=str(module_path),joint_resource=True,
        cx=sum(o.kind=='CX' for o in nops),ticks=max(o.time for o in nops)+1)
    return c,meta

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('stem');ap.add_argument('--module');ap.add_argument('--price',action='store_true');a=ap.parse_args()
    c,meta=integrate(a.stem,a.module);name='joint_end_'+Path(a.stem).name.split('_d0_')[0]
    stem=write_stem(c.text(),D,HERE/'cand',name,source=meta);r=dict(stem=str(stem),**meta,raw=raw_check(c.text(),D))
    print(json.dumps(r,indent=2),flush=True)
    if a.price and r['raw']['ok']:r['price']=price(stem,processes=1);print(json.dumps(r['price'],indent=2),flush=True)
    stem.with_suffix('.result.json').write_text(json.dumps(r,indent=2)+'\n')
