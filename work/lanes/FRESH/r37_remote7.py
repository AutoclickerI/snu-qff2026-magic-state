from r37 import *
orig,dets,md=load(BASE);stems=[]
for phase in (False,True):
 for start in (19,20):
  oo=[]
  for o in orig:
   if (o.bit in (7,275) or (o.kind=='RX' and o.qs==(8,) and o.time==22) or (o.kind=='R' and o.qs==(13,) and o.time==19) or (o.kind=='CX' and o.qs==(7,13) and o.time in (20,23))):continue
   oo.append(copy.deepcopy(o))
  for o in oo:
   if o.time>=23:o.time-=1
  gates=[f.Op('RX',(13,),start-1),f.Op('CX',(13,7),start),f.Op('CX',(7,8),21),f.Op('CX',(13,7),22),f.Op('MX',(13,),23,7)]
  if phase:
   # S7 commutes with middle CX7->8; bracket the whole bus word to turn both end gates into CY.
   if start==20:
    # q7 busy18/19; use diagonal S before the unchanged first-half cat CXs and undo its propagated phase is unsafe.
    # Need make a slot by sliding the inverse's CX8->7 from23 to24 and front CX8->7 from19 to18 where legal; tested separately.
    pass
   gates.extend([f.Op('SDG',(7,),start-1),f.Op('S',(7,),23)])
  if any(set(g.qs)&set(o.qs) and g.time==o.time for g in gates for o in oo):print('CONFLICT',phase,start,flush=True);continue
  dd=[r.copy() for r in dets if 275 not in r]
  s=emit37(f'remote7_{int(phase)}_{start}',oo+gates,dd,dict(md,R=43),dict(remote_copy=[13,7,8],phase_bus=phase,start=start))
  r=audit(s);print('AUDIT',s.name,r.get('c1'),r.get('error'),r.get('static',{}).get('prediction'),flush=True)
  if r.get('c1',1)<1e-12 and r['static']['general_atoms']==0:stems.append(str(s))
(D/'remote7_stems.json').write_text(json.dumps(stems,indent=2))
