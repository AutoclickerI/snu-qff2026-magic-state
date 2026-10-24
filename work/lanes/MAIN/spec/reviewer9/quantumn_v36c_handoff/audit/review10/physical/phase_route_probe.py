"""Matched routing-only comparison using the published TREP2 beam router.
No full circuit, noise score or re-prepared resource is asserted.
"""
import ast,json,random,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parent
src=(ROOT/'sources/work__lanes__TREP2__forms.py').read_text()
tree=ast.parse(src)
nodes=[]
for n in tree.body:
 if isinstance(n,ast.FunctionDef) and n.name in ('route','network'):nodes.append(n)
g={'random':random,'CELLS':[0,1,2,3,4,6,7,8,9,10,13,14,15,19,20]}
g['DATA']=[0,20,7,4,3,15,8]
g['EDGES']=[(i,j)for i,q in enumerate(g['CELLS'])for j,v in enumerate(g['CELLS'])if abs(q//6-v//6)+abs(q%6-v%6)==1]
exec(compile(ast.Module(body=nodes,type_ignores=[]),'<pinned TREP2 functions>','exec'),g)
enum=json.loads((ROOT/'sources/work__lanes__TREP__enumeration.json').read_text())
chosen=[next(f for f in enum['forms']if f['id']==k)for k in ['f00_0','f14_1']]
chosen[1]['signed_representations']=[{'coefficients':[-1]*14}]
results=[]
for form in chosen:
 g['ROWS']=dict(zip(g['DATA'],[2,31,4,21,14,19,8]));g['ROWS'][6]=16 if form['T']==15 else 0
 for seed in range(100):
  try:
   ops,ncx=g['network'](form,seed)
   free={q:0 for q in g['CELLS']}
   for op,a,b in ops:
    qs=[a,b]if op=='cx'else[a];t=max(free[q]for q in qs)
    for q in qs:free[q]=t+1
   row={'form':form['id'],'T':form['T'],'seed':seed,'compute_uncompute_CX':ncx,'phase_fragment_ASAP_ticks':max(free.values()),'operations':ops}
  except RuntimeError as e:row={'form':form['id'],'seed':seed,'error':str(e)}
  results.append(row)
 (ROOT/'phase_route_certificate.json').write_text(json.dumps({'scope':__doc__,'trials':100,'results':results},indent=2))
 valid=[r for r in results if r['form']==form['id']and'error'not in r]
 print(json.dumps({'form':form['id'],'valid':len(valid),'best_by_CX':{k:v for k,v in min(valid,key=lambda r:(r['compute_uncompute_CX'],r['phase_fragment_ASAP_ticks'])).items()if k!='operations'},'best_by_depth':{k:v for k,v in min(valid,key=lambda r:(r['phase_fragment_ASAP_ticks'],r['compute_uncompute_CX'])).items()if k!='operations'}}),flush=True)
