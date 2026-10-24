from round35 import *
from r36_static import diagnostic
OUT=HERE/'r36';BASE36=ROOT/'work/lanes/MAIN/v35b'
# Transversal Clifford gauges around the check round. Gate noise and schedule preserved.
ops,dets,md=load(BASE36);data=md['data_qubits'];A=[1,14,8,9,2,16,15]
rows=[]
for kind,inv in [('S','SDG'),('SDG','S'),('H','H'),('SX','SXDG'),('SXDG','SX')]:
 oo=copy.deepcopy(ops);mods=[]
 for q in data:
  a=A[data.index(q)];t=max(o.time for o in oo if o.kind=='CX' and o.qs==(q,a))-1
  conflicts=[o for o in oo if o.time==t and q in o.qs]
  if conflicts:
   assert len(conflicts)==1 and conflicts[0].kind in ('T','TDG');assert not any(o.time==t-1 and q in o.qs for o in oo);conflicts[0].time-=1;mods.append((q,t,t-1))
  oo.extend([f.Op(kind,(q,),t),f.Op(inv,(q,),46)])
 stem=emit('gauge_'+kind.lower(),oo,copy.deepcopy(dets),md,dict(base=str(BASE36),gauge=kind,retimings=mods))
 r=dict(stem=str(stem),kind=kind)
 try:
  r['ideal']=certify(stem);st=diagnostic(stem);r['static']={k:st[k] for k in ('total_atoms','failed_atoms','bad_gates')};(OUT/(stem.name+'.static.json')).write_text(json.dumps(st,indent=2))
  r['speed']=speed(stem,10000)
 except Exception as ex:r['error']=repr(ex)
 rows.append(r);print(json.dumps({k:v for k,v in r.items() if k!='ideal'}),flush=True)
(OUT/'gauges.json').write_text(json.dumps(rows,indent=2))
