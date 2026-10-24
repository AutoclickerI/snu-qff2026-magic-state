from round35 import *
from r36_static import diagnostic
OUT=HERE/'r36';src=ROOT/'work/lanes/MAIN/v35b';ops,dets,md=load(src)
old=[o for o in ops if o.kind=='RX' and o.qs==(8,) and o.time==22];assert len(old)==1
ops.remove(old[0])
for o in ops:
 if o.time>22:o.time-=1
md['R']=43
s=emit('v35b_reuse8',ops,dets,md,dict(base=str(src),removed_reset=[8,22],retained_MX_flag=7,source='XTIM q8-reuse mechanism ported to v35b'))
print('IDEAL',certify(s),flush=True);st=diagnostic(s);(OUT/'v35b_reuse8.static.json').write_text(json.dumps(st,indent=2));print('STATIC',st['failed_atoms'],st['bad_gates'],flush=True);print('SPEED',speed(s,10000),flush=True);print('PRICE',price(s,10),flush=True)
