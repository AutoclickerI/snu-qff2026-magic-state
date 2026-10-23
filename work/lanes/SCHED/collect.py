import json,glob,os
from pathlib import Path
rows=[]
for f in glob.glob('work/lanes/SCHED/encoders/enc_*.exact.json'):
 j=json.load(open(f)); n=Path(f).stem.rsplit('.',1)[0]; m=json.load(open(Path(f).with_name(n+'.json')))
 enc=m.get('encoder',{})
 rows.append(dict(name=n,**j,encoder_danger=enc.get('danger'),encoder_depth=enc.get('depth'),encoder_cx=enc.get('cx')))
rows.sort(key=lambda x:x['loss2']);Path('work/lanes/SCHED/encoder_second.json').write_text(json.dumps(rows,indent=2)+'\n');print(len(rows));print(*[(r['name'],r['loss2'],r['encoder_danger'],r['encoder_depth']) for r in rows[:10]],sep='\n')
