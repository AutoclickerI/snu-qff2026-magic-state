"""Checked physical |0> after destructive X readout can be a hop destination."""
import json,re
from pathlib import Path
from build import build
from reuse_A import reuse
from retime import run
H=Path(__file__).resolve().parent

def physical_zero(stem,out):
 p=json.loads(Path(stem).with_suffix('.plan.json').read_text());basis={}
 for l in p['tail']:
  v=sum(1<<int(b)for b in re.findall(r'c\[(\d+)\]',l))
  while v:
   k=v.bit_length()-1
   if k not in basis:basis[k]=v;break
   v^=basis[k]
 prev={};ops=[];changed=[]
 for o in sorted(p['ops'],key=lambda o:o['t']):
  q=o['qs'][0];old=prev.get(q)
  if o['region']=='data_hops'and o['name']=='RESET'and q in(15,16)and old and old['name']in('MX','MEASURE')and old['lines'][-1].startswith('measure '):
   b=int(re.findall(r'c\[(\d+)\]',' '.join(old['lines']))[0]);v=1<<b
   while v and v.bit_length()-1 in basis:v^=basis[v.bit_length()-1]
   assert v==0;changed.append(dict(cell=q,certified_record=b,previous_lines=old['lines'],physical_post_basis='Z',removed_reset_time=o['t']));continue
  ops.append(o)
  for qq in o['qs']:prev[qq]=o
 p['ops']=ops;p['meta']['checked_physical_zero_destination']=changed;temp=H/(out+'_ordered');temp.with_suffix('.plan.json').write_text(json.dumps(p,indent=1));run(temp,out);print(changed,flush=True)
for ai in(2,6):
 stem=build(H/'r2_d11_k56.prep.json',f'region2_early_A{ai}',a_prep=H/f'A2_top{ai}.json',hop_t=True)
 p=json.loads(stem.with_suffix('.plan.json').read_text());safe=[]
 for q in p['meta']['A']:
  own=[o for o in p['ops']if o['region']=='A'and o['qs']==[q]];ini=own[0];previous=[o for o in p['ops']if q in o['qs']and o['t']<ini['t']]
  if previous and previous[-1]['name']in('MX','MEASURE')and(ini['name']=='RX')==(previous[-1]['name']=='MX'):safe.append(q)
 name=stem.name+'_safe';reuse(stem,name,safe);physical_zero(H/name,name+'_zero')
(H/'early_stems.json').write_text(json.dumps([f'region2_early_A{i}_safe_zero'for i in(2,6)]))
