from pathlib import Path
import json
from core import *
from moves import init_moves,readout_moves
OUT=Path(__file__).resolve().parent
src=OUT/'compose_families_v25k_8d88ea5acd';base=read(src)
# Make metadata exact row visible.
r=json.loads((src.with_suffix('.exact.json')).read_text());(OUT/'best_q19check.exact.json').write_text(json.dumps(r,indent=2));m=json.loads(src.with_suffix('.json').read_text());(OUT/'best_q19check.json').write_text(json.dumps(m,indent=2))
cs=[]
for c,d in readout_moves(base):
 if d.get('move')=='add_edge' and d.get('edge') in ([14,15],[14,8]):d['parent_total']=r['total'];d['local_track']=True;cs.append((c,d))
# q11 reset-to-measure and q19 mx-init alternative; then add readout to q11 candidate.
q11=None
for c,d in init_moves(base):
 if d.get('move')=='reset_to_measure' and d.get('q')==11:q11=c;d['parent_total']=r['total'];d['local_track']=True;cs.append((c,d))
 if d.get('move')=='mx_init_pivots' and d.get('units')==[151]:d['parent_total']=r['total'];d['local_track']=True;cs.append((c,d))
if q11:
 for c,d in readout_moves(q11):
  if d.get('move')=='add_edge' and d.get('edge') in ([14,15],[14,8]):d['parent_total']=r['total'];d['local_track']=True;cs.append((c,d))
print('cands',len(cs));batch(cs,'target_combos_v25k',8)
