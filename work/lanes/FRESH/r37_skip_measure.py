from r37 import *
ops,dets,md=load(BASE)
for extra in [False,True]:
 oo=[copy.deepcopy(o) for o in ops if o.bit!=7 and not(o.kind=='RX' and o.qs==(8,) and o.time==22)]
 if extra:
  # Later X read at q2 becomes the standalone projection; second cat flag stays unchanged.
  oo=[o for o in oo if o.bit!=10]
 dd=[]
 for row in dets:
  rr=row-{7}-({10} if extra else set())
  if rr and rr not in dd:dd.append(rr)
 s=emit37('skip8_both'+('_and2' if extra else ''),oo,dd,md,dict(drop_MX8=True,drop_RX8=True,later_X2_projector=not extra))
 r=audit(s);print('AUDIT',json.dumps({k:v for k,v in r.items() if k not in ('ideal','static','harmful_singles','trace')}),flush=True);print('STATIC',r.get('static',{}).get('prediction'),flush=True)
 if r.get('harmful_singles'):print('HARM',r['harmful_singles'][:3],flush=True)
 if r.get('c1',1)<1e-12:print('PRICE',price(s,7),flush=True);print('SPEED',speed(s,10000),flush=True)
