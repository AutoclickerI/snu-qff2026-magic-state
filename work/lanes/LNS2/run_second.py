from pathlib import Path
import json
from core import *
from moves import init_moves,readout_moves
out=Path(__file__).resolve().parent;src=out/'target_combos_v25k_0d713c0861';base=read(src);r=json.loads((src.with_suffix('.exact.json')).read_text());(out/'best_second.exact.json').write_text(json.dumps(r,indent=2));m=json.loads(src.with_suffix('.json').read_text());(out/'best_second.json').write_text(json.dumps(m,indent=2));cs=[]
for fn in [init_moves,readout_moves]:
 for c,d in fn(base):d['parent_total']=r['total'];d['local_track']=True;cs.append((c,d))
print('cands',len(cs),flush=True);batch(cs,'second_families_v25k',8)
