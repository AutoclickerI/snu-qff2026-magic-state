from pathlib import Path
import json
from core import *
from moves import init_moves,timing_moves,commute_moves,readout_moves
OUT=Path(__file__).resolve().parent

def save(name,c,desc):
 c=normalize(c);m=dict(c['meta']);m.update(method=desc,source=str(c.get('source','')),lns_result=dict(stem=name,desc=desc));(OUT/(name+'.qasm')).write_text(textof(c));(OUT/(name+'.json')).write_text(json.dumps(m,indent=2)+'\n');return c
rv=read(OUT/'review5_v25k'); save('safe_review_base',rv,'reviewer-copy4-corrected')
# timing and commuting on reviewer base
rt=next(c for c,d in timing_moves(rv,True) if d.get('op')==['cx q[10],q[4];'] and d.get('new')==10);save('safe_review_timing10',rt,'reviewer+timing_q10q4_t10')
for j,(c,d) in enumerate(commute_moves(rt)):
 if d.get('ops')==[['cx q[1],q[0];'],['cx q[1],q[7];']]: save(f'safe_review_timing_commute{j}',c,f'reviewer+timing+commute_q1_{j}')
# Choose the last variant in native order by exact scans below; retain all files.
# q19 check, then q11 reset-to-measure, then edge 14->15.
base=read(OUT/'safe_review_timing_commute52') if (OUT/'safe_review_timing_commute52.qasm').exists() else rt
q19=next(c for c,d in init_moves(base) if d.get('move')=='check_rx' and d.get('q')==19);save('safe_q19check',q19,'reviewer+timing+commute+q19check')
q11=next(c for c,d in init_moves(q19) if d.get('move')=='reset_to_measure' and d.get('q')==11);save('safe_q19_q11',q11,'reviewer+timing+commute+q19check+q11reset')
edge=next(c for c,d in readout_moves(q11) if d.get('move')=='add_edge' and d.get('edge')==[14,15]);save('safe_best',''.join([]) and edge or edge,'reviewer+timing+commute+q19check+q11reset+edge14to15')
print('saved')
