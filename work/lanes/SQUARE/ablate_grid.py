import sys,json
from build_rounds import H

name=sys.argv[1];stem=H/'builds'/name
m=json.loads(stem.with_suffix('.json').read_text());R=m['round_start'];first={}
for t,a,b in m['preparation_ops']:
    for q in (a,b):first[q]=min(first.get(q,9999),t-1)
rows=[]
for tag,extra in [('perfectprep',dict(perfect_resource=first)),('perfectwait',dict(perfect_data_wait=[44,R])),
                  ('perfectboth',dict(perfect_resource=first,perfect_data_wait=[44,R])),('roundonly',dict(noise_start=R))]:
    n=name+'_'+tag;p=H/'builds'/n
    p.with_suffix('.qasm').write_text(stem.with_suffix('.qasm').read_text())
    p.with_suffix('.json').write_text(json.dumps(dict(m,**extra,change=f'{name}: {tag} counterfactual, same circuit and schedule'),indent=2)+'\n');rows.append(n)
(H/'ablation_manifest.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
