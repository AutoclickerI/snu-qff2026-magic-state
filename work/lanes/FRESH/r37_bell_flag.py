from r37 import *
orig,dets,md=load(BASE);stems=[]
for end in (22,23):
 for cleanup in (False,True):
  oo=[]
  for o in orig:
   if (o.bit in (7,275) or (o.kind=='RX' and o.qs==(8,) and o.time==22) or (o.kind=='R' and o.qs==(13,) and o.time==19) or (o.kind=='CX' and o.qs==(7,13) and o.time in (20,23))):continue
   oo.append(copy.deepcopy(o))
  for o in oo:
   if o.time>=23:o.time-=1
  if end==23:
   # Move inverse CX8->14 later to free bus14 for the remote check close.
   for o in oo:
    if o.kind=='CX' and o.qs==(8,14) and o.time==24:o.time=25
    if o.kind=='CX' and o.qs==(2,8) and o.time==25:o.time=26
    if o.bit==10:o.time=27
  uend=end+1
  gates=[f.Op('RX',(13,),16),f.Op('R',(12,),16),f.Op('CX',(13,12),17),f.Op('CX',(13,14),19),f.Op('CX',(7,13),20),f.Op('CX',(14,8),21),f.Op('CX',(7,13),end),f.Op('CX',(13,14),uend),f.Op('CX',(13,12),uend+1),f.Op('MX',(13,),uend+2,7),f.Op('M',(12,),uend+2,275)]
  if cleanup:gates.append(f.Op('CX',(14,8),uend+1))
  try:
   s=emit37(f'bellflag_{end}_{int(cleanup)}',oo+gates,copy.deepcopy(dets),dict(md,R=43),dict(base='MAIN/v36b',remote_flag='X8 via13,14',Bell=[13,12],q7_guard=[20,end],cleanup=cleanup))
   r=audit(s);print(s.name,'c1',r.get('c1'),'error',r.get('error'),'static',r.get('static',{}).get('prediction'),flush=True)
   if r.get('harmful_singles'):print('HARM',r['harmful_singles'][:3],flush=True)
   if r.get('c1',1)<1e-12 and r['static']['general_atoms']==0:stems.append(str(s))
  except Exception as ex:print('ERROR',end,cleanup,repr(ex),flush=True)
(D/'bell_stems.json').write_text(json.dumps(stems,indent=2))
