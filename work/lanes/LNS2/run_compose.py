from pathlib import Path
import json
from core import *
from moves import init_moves,phase_moves,readout_moves
out=Path(__file__).resolve().parent
base=read(out/'review5_q8_commute52_timing10')
parent=json.loads((out/'current_best_composite.exact.json').read_text())['total'];cs=[]
for fn in [init_moves,phase_moves,readout_moves]:
 for c,d in fn(base):d['parent_total']=parent;d['local_track']=True;cs.append((c,d))
print('generated',len(cs),flush=True);batch(cs,'compose_families_v25k',8)
