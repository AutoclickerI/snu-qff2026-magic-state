from common import *
from guards import catalog,apply
from knapsack import compatible

inputs = {
 'R37': P/'joint/region2_early_A2_safe_zero',
 'R37selective': P/'joint/region2_selectiveT',
 'R39': P/'joint/region2_k56_A2_safe',
}
packages = json.loads((H/'control_R38.knapsack_queue.json').read_text())
out=[]
for label,path in inputs.items():
 p=load(path);base='control_'+label
 save(p,base);acts=catalog(p)
 for i,name in enumerate(packages):
  selected=json.loads((H/(name+'.json')).read_text())['protection_actions'];chosen=[];miss=[]
  for old in selected:
   matches=[a for a in acts if a['type']==old['type'] and a.get('q')==old.get('q') and a.get('h')==old.get('h') and a.get('axis')==old.get('axis')]
   matches.sort(key=lambda a: sum(abs(a.get(k,0)-old.get(k,0))for k in ('t','first','last')if a.get(k)is not None and old.get(k)is not None))
   found=next((a for a in matches if a not in chosen and compatible(p,chosen+[a])),None)
   if found is None:miss.append(old)
   else:chosen.append(found)
  z=apply(p,chosen);z['meta']['package_port']=dict(from_package=name,matched=len(chosen),missing=miss,selection='closest matching physical action, then full reprice; transferred marginal gains are not assumed')
  stem=save(z,label+f'_pack{i:02d}');out.append(stem.name)
(H/'ported_packages_queue.json').write_text(json.dumps(out));print('ported packages',len(out),flush=True)
