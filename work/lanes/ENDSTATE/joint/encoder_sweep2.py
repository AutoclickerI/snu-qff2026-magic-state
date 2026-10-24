import json
from pathlib import Path
from build import build
from reuse_A import reuse
from retime import run
H=Path(__file__).resolve().parent;rows=json.loads((H/'A2_exact_raw.json').read_text())['top'];out=[]
for i,ap in enumerate(rows):
 ap['cx']=sum(map(len,ap['ops']));f=H/f'A2_top{i}.json';f.write_text(json.dumps(ap));name=f'region2_k56_A{i}';stem=build(H/'r2_d11_k56.prep.json',name,a_prep=f);name+='_safe'
 # Reuse only sources whose previous measurement basis agrees with the desired source basis.
 p=json.loads(stem.with_suffix('.plan.json').read_text());safe=[]
 for q in p['meta']['A']:
  own=[o for o in p['ops']if o['region']=='A'and o['qs']==[q]];ini=own[0];prev=[o for o in p['ops']if q in o['qs']and o['t']<ini['t']]
  if prev and prev[-1]['name']in('MX','MEASURE')and(ini['name']=='RX')==(prev[-1]['name']=='MX'):safe.append(q)
 reuse(stem,name,safe);out.append(name)
(H/'encoder_sweep2_stems.json').write_text(json.dumps(out))
