from round35 import *
# Exhaust fixed-A subset masks, including all proper nonempty subsets.
base,dets,md=load(BASE);full,_,_=load(D/'sx_full');data=md['data_qubits'];rows=[]
for mask in range(128):
 qs={q for i,q in enumerate(data) if mask>>i&1};oo=copy.deepcopy(base)
 for q in qs:
  sx=next(o for o in full if o.kind=='SX' and o.qs==(q,))
  for o in oo:
   if o.qs==(q,) and o.time==sx.time and o.kind in ('T','TDG'):o.time-=1
  oo.extend([copy.deepcopy(sx),f.Op('SXDG',(q,),46)])
 oo.sort(key=lambda o:o.time);f.DATA=data
 try:
  m=f.make_model(oo,dets);e=f.Engine(m);a,n=e.ntable(0,0)
  valid=bool(abs(a-1)<1e-10 and abs(n[0])<1e-10)
  rows.append(dict(mask=mask,qubits=sorted(qs),valid=valid,acceptance=a,loss=float(n[0])))
 except AssertionError as ex:rows.append(dict(mask=mask,qubits=sorted(qs),valid=False,reason=str(ex)))
(D/'sx_subset_certificate.json').write_text(json.dumps(rows,indent=2));print('VALID',[r['mask'] for r in rows if r['valid']],flush=True)
