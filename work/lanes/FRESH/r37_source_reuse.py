from r37 import *
orig,dets,md=load(BASE);out=[]
for q,t,kind in [(14,37,'drop'),(8,36,'H'),(9,38,'H'),(16,39,'H'),(2,36,'H'),(2,28,'drop'),(9,32,'H')]:
 oo=copy.deepcopy(orig);target=next(o for o in oo if o.qs==(q,) and o.time==t and o.kind in ('R','RX'))
 if kind=='drop':oo.remove(target)
 else:target.kind='H'
 s=emit37(f'reuse_{q}_{t}',oo,copy.deepcopy(dets),md,dict(source_reuse=[q,t,kind],base='MAIN/v36b'))
 r=audit(s);print(s.name,'c1',r.get('c1'),'error',r.get('error'),'atoms',r.get('static',{}).get('general_atoms'),flush=True)
 if r.get('c1',1)<1e-12 and r['static']['general_atoms']==0:out.append(str(s))
(D/'source_reuse_stems.json').write_text(json.dumps(out,indent=2))
