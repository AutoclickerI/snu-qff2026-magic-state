from r37 import *
# Extend the borrowed-cat Y guard through the last idle before inverse-cat return.
orig,dets,md=load(D/'remote3_flag13');out=[]
for helper in (1,6):
 for aa,bb in [(20,22),(20,23),(21,23)]:
  for meas in ('keep','early'):
   oo=copy.deepcopy(orig)
   if helper==6:
    for o in oo:
     if o.kind=='CX' and o.qs==(7,6) and o.time==24:o.time=25
   gates=[f.Op('SDG',(helper,),aa-1),f.Op('CX',(7,helper),aa),f.Op('CX',(7,helper),bb),f.Op('S',(helper,),bb+1)]
   if any(set(g.qs)&set(o.qs) and g.time==o.time for g in gates for o in oo):continue
   oo+=gates
   if meas=='early':
    # Measure the remote flag immediately after its closing CX; other inverses commute.
    o=next(o for o in oo if o.bit==7);o.time=23
   name=f'catguard_{helper}_{aa}_{bb}_{meas}'
   try:
    s=emit37(name,oo,copy.deepcopy(dets),md,dict(base='remote3_flag13',borrowed_guard=[helper,aa,bb],measurement=meas));r=audit(s)
    print(name,r.get('c1'),r.get('error'),r.get('static',{}).get('prediction'),flush=True)
    if r.get('c1',1)<1e-12 and r['static']['general_atoms']==0:out.append(str(s))
   except Exception as ex:print('ERROR',name,repr(ex),flush=True)
(D/'cat_more_stems.json').write_text(json.dumps(out,indent=2))
