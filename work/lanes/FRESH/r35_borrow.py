from round35 import *
source=D/'feedback_best';ops,dets,md=load(source);rows=[]
for axis in ('X','Z'):
 for aa,bb in ((39,41),(39,40),(40,41)):
  oo=copy.deepcopy(ops);edge=(10,9) if axis=='X' else (9,10)
  oo.extend([f.Op('CX',edge,aa),f.Op('CX',edge,bb)])
  stem=emit(f'borrow9_{axis}_{aa}_{bb}',oo,copy.deepcopy(dets),md,dict(source=str(source),borrowed_echo=[10,9,axis,aa,bb]))
  r=dict(stem=str(stem))
  try:certify(stem);r.update(price(stem,7))
  except Exception as e:r['error']=repr(e)
  rows.append(r);print(json.dumps(r),flush=True)
(D/'borrow_results.json').write_text(json.dumps(rows,indent=2))
