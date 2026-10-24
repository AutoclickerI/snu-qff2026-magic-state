import json,time
from pathlib import Path
from timing import schedule
H=Path(__file__).resolve().parent;rows=json.loads((H/'labelled_regions.json').read_text())
for depth in (9,10):
 out=[]
 for i,row in enumerate(rows):
  r=schedule(row,depth,0);r['row_index']=i;out.append(r)
 (H/f'timed_regions_d{depth}.json').write_text(json.dumps(out,indent=1));print(depth,len(out),min(x.get('R',999)for x in out),flush=True)
