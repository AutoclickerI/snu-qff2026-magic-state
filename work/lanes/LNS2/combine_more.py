import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from core import *;from moves import timing_moves,commute_moves
OUT=Path(__file__).resolve().parent
for src,name in [('review5_q8_commute52','review5_q8_commute52_timing10'),('review5_q8_timing10','review5_q8_timing10_commute52')]:
 b=read(OUT/src); 
 if 'timing' in name and src.endswith('commute52'):
  c=next(c for c,d in timing_moves(b,True) if d.get('op')==['cx q[10],q[4];'] and d.get('new')==10); desc='review+q8+commute52+timing10'
 else:
  c=next(c for c,d in commute_moves(b) if d.get('ops')==[['cx q[1],q[0];'],['cx q[1],q[7];']] and d.get('old')==[37,38]); desc='review+q8+timing10+commute52'
 c=normalize(c);m=dict(c['meta']);m.update(method=desc,source=str(OUT/src),lns_result=dict(stem=name,desc=desc));(OUT/(name+'.qasm')).write_text(textof(c));(OUT/(name+'.json')).write_text(json.dumps(m,indent=2)+'\n');print(name)
