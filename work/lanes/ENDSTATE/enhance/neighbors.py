from common import *
from guards import apply
from knapsack import compatible
import collections

def run(parent,tag):
 meta=json.loads((H/(parent+'.json')).read_text());base_name=meta.get('search_base','control_R38');base=load(H/base_name);catalog=json.loads((H/(base_name+'.actions.json')).read_text());byid={a['id']:a for a in catalog};selected={a['id']for a in meta['protection_actions']};seen={tuple(sorted(selected))};proposals=[]
 def add(ids,move):
  key=tuple(sorted(ids))
  if key in seen:return
  seen.add(key);aa=[byid[i]for i in key]
  if not compatible(base,aa):return
  p=apply(base,aa);p['meta'].update(search_base=base_name,search_parent=parent,search_move=move);stem=save(p,tag+f'_{len(proposals):03d}');proposals.append(stem.name)
 for i in selected:add(selected-{i},dict(remove=[i]))
 for i,a in byid.items():
  if i in selected:continue
  conflicts={j for j in selected if not compatible(base,[a,byid[j]])}
  if len(conflicts)<=2:add((selected-conflicts)|{i},dict(insert=i,remove=sorted(conflicts)))
 groups=collections.defaultdict(set)
 for i in selected:
  a=byid[i];groups['type:'+a['type']].add(i)
  if a['type']=='echo':groups['helper:'+str(a['h'])].add(i)
  if a['type']=='measured_Z_init':
   seq=[o for o in base['ops']if a['q']in o['qs']and o['t']<a['t']]
   if seq:
    prev=max(seq,key=lambda o:o['t'])
    if prev['name']=='MX'and prev['lines'][-1].startswith('measure '):groups['native_MX_boundary:'+str(prev['t'])].add(i)
 for label,ids in groups.items():
  if len(ids)>1:add(selected-ids,dict(remove_group=label,remove=sorted(ids)))
 (H/(tag+'.queue.json')).write_text(json.dumps(proposals));(H/(tag+'.scope.json')).write_text(json.dumps(dict(parent=parent,base=base_name,single_removal=True,single_insertion_max_conflict_removal=2,group_removals=list(groups),candidates=len(proposals)),indent=2));print(tag,len(proposals),flush=True)
if __name__=='__main__':run(*sys.argv[1:])
