"""Reuse coherent-hop zero sources directly as zero inputs to A."""
from common import *
import importlib.util
from decoder import options,build
spec=importlib.util.spec_from_file_location('endstate_retime',P/'joint/retime.py');rt=importlib.util.module_from_spec(spec);spec.loader.exec_module(rt);rt.H=H
base=load(H/'control_R38');out=[]
for label,cells in [('27',[27]),('15_27',[15,27]),('14_15_27',[14,15,27])]:
 p=copy.deepcopy(base);removed=[]
 for q in cells:
  reuse=[r for r in p['meta']['A_reuse']if r['cell']==q];assert len(reuse)==1 and reuse[0]['old']=='RESET'and reuse[0]['replacement']=='none'
  found=[o for o in p['ops']if o['region']=='data_hops'and o['name']=='MEASURE'and o['qs']==[q]];assert len(found)==1;o=found[0];b=int(re.search(r'c\[(\d+)\]',o['lines'][0])[1]);rows=[i for i,l in enumerate(p['tail'])if b in map(int,re.findall(r'c\[(\d+)\]',l))];assert len(rows)==1 and p['tail'][rows[0]]==f'// DETECTOR c[{b}]'
  prior=max((a for a in p['ops']if q in a['qs']and a['t']<o['t']),key=lambda a:a['t']);assert prior['name']=='CX'and prior['qs'][1]==q
  p['ops'].remove(o);p['tail'].pop(rows[0]);removed.append(dict(cell=q,bit=b,last_hop_CX=prior['qs'],time=o['t']))
 p['meta']['removed_hop_guards']=removed;p['meta']['guard_removal_scope']='The second coherent-hop CX leaves this source |0>; it becomes an A zero input. Existing full-circuit correctness/score gates are retained; no claim of equal noise.'
 name='prune'+label;temp=H/(name+'_ordered');temp.with_suffix('.plan.json').write_text(json.dumps(p,indent=1));rt.run(temp,name);p=load(H/name);save(p,name);out.append(name)
 # Exhaust all native two-CX logical flags on the pruned interface first.
 for i,opt in enumerate(options(p['meta']['A'])):
  if opt['cx']!=2:continue
  s=build(p,opt,name+f'_dec{i:03d}')
  if s is not None:out.append(s.name)
(H/'pruned_candidates.json').write_text(json.dumps(out,indent=2));print('pruned and decoder candidates',len(out),flush=True)
