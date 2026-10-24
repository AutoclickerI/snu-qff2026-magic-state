from r37 import *
src=D/'remote3_flag13';ops,dets,md=load(src);stems=[]
for helper in (1,6):
 for aa,bb in ((20,21),(20,22),(19,21),(18,21)):
  oo=copy.deepcopy(ops);gates=[f.Op('SDG',(helper,),aa-1),f.Op('CX',(7,helper),aa),f.Op('CX',(7,helper),bb),f.Op('S',(helper,),bb+1)]
  if any(set(g.qs)&set(o.qs) and g.time==o.time for g in gates for o in oo):continue
  oo+=gates
  try:
   s=emit37(f'catY_{helper}_{aa}_{bb}',oo,copy.deepcopy(dets),md,dict(base=str(src),guard=['CY',7,helper,aa,bb],mechanism='Borrow cat helper and reuse its deterministic terminal MX as phase-error flag'))
   r=audit(s);print(s.name,'c1',r.get('c1'),'error',r.get('error'),'static',r.get('static',{}).get('prediction'),flush=True)
   if r.get('c1',1)<1e-12 and r['static']['general_atoms']==0:stems.append(str(s))
  except Exception as ex:print('ERROR',helper,aa,bb,repr(ex),flush=True)
(D/'cat_echo_stems.json').write_text(json.dumps(stems,indent=2))
