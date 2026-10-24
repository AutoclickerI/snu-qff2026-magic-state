import json,re
from pathlib import Path
P=Path('/home/jihoon/competitions/quantumn')/'work/lanes/PRE3'
rows=[]
for st in ['base','q13_19','q19_13_prompt','active']:
 t=(P/(st+'.exact.txt')).read_text(); get=lambda pat: (float(re.search(pat,t).group(1)) if re.search(pat,t) else None)
 row={'variant':st,'c1':get(r'first order : c1 p = ([0-9.e+-]+)'), 'second':get(r'second order: ([0-9.e+-]+)'), 'third':get(r'third order: ([0-9.e+-]+)'), 'total':get(r'1-F \(to 3rd order\) = ([0-9.e+-]+)'), 'exp_A1':get(r'exp\(-A1\) = ([0-9.e+-]+)'), 'check':json.loads((P/(st+'.check.json')).read_text())}
 m=P/(st+'.mc.json'); row['mc']=json.loads(m.read_text()) if m.exists() else None;rows.append(row)
(P/'scores.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows,indent=2))
