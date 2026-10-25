"""Reuse SQUARE's completed grid routing, transplant v37b's causal prefix,
and replace its terminal instrument by the enumerated opposite square shear.
The other lane is read only; all resulting artifacts live in ENDSEARCH.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json
from build_candidates import H,prefix,parse_current,finish,save
old=json.loads((H/'inputs/square_prefix.json').read_text())
m=json.loads((H/'inputs/square_grid.json').read_text())
ops,dets=parse_current((H/'inputs/square_grid.qasm').read_text())
key=lambda o:(o.kind,tuple(o.qs),o.time,o.bit)
oldkeys={(o['kind'],tuple(o['qs']),o['time'],o['bit']) for o in old['kept_operations']}
oldpd={tuple(sorted(d)) for d in old['detectors']}
R=m['round_start'];c,D,release=prefix();mapping={};suffix=[]
for o in ops:
    if key(o) in oldkeys:continue
    if o.time>=R:continue
    suffix.append(o)
for o in suffix:
    if o.kind=='CX':c.cx(o.time,*o.qs)
    elif o.kind in ('R','RX'):c.reset(o.time,o.qs[0],o.kind=='RX')
    elif o.kind in ('M','MX'):
        mapping[o.bit]=c.read(o.time,o.qs[0],o.kind=='MX')
        if o.kind=='MX' and any(v.time>o.time and o.qs[0] in v.qs for v in suffix):c.add(o.time,f'h q[{o.qs[0]}];')
    else:c.add(o.time,f'{o.kind.lower()} q[{o.qs[0]}];')
measures={o.bit:o for o in ops if o.bit is not None}
for d in dets:
    if tuple(sorted(d)) in oldpd:continue
    if any(measures[b].time>=R for b in d):continue
    c.dets.append([mapping.get(b,b) for b in sorted(d)])
t=json.loads((H/'choices.json').read_text())['square'];blocks=[m['roles'][k] for k in ('D','A','B','C')]
finish(c,t,blocks,R)
name=save(c,'grid_square_v37b',t,blocks,round_start=R,change='v37b causal prefix; SQUARE completed grid route and storage guards; enumerated A->C square instrument',grid_source='inputs/square_grid.qasm')
p=H/'builds'/f'{name}.json';md=json.loads(p.read_text());md['grid_free']=False;p.write_text(json.dumps(md,indent=2)+'\n')
ops,ds=parse_current(p.with_suffix('.qasm').read_text());bits={o.bit for o in ops if o.bit is not None}
assert all(set(d)<=bits for d in ds)
for o in ops:
    if o.kind=='CX':
        a,b=o.qs;assert abs(a//6-b//6)+abs(a%6-b%6)==1,o
print(name,flush=True)
