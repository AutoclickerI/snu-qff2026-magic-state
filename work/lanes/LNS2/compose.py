import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from core import *
from moves import init_moves,timing_moves,commute_moves
OUT=Path(__file__).resolve().parent

def savec(name,c,desc):
 c=normalize(c);m=dict(c['meta']);m.update(method=desc.get('move',name),source=str(c.get('source','')),lns_result=dict(stem=name,desc=desc));(OUT/(name+'.qasm')).write_text(textof(c));(OUT/(name+'.json')).write_text(json.dumps(m,indent=2)+'\n');return name
q8=read(OUT/'choices_v25k_6dd3b41bd4')
# q8 + timing, and then q8 + timing + each compatible commute swap
qt=next(c for c,d in timing_moves(q8,True) if d.get('op')==['cx q[10],q[4];'] and d.get('old')==12 and d.get('new')==10)
savec('combo_q8_timing10',qt,dict(family='compose',move='q8reuse+timing_q10q4_t10'))
for j,(c,d) in enumerate(commute_moves(qt)):
 if d.get('ops')==[['cx q[1],q[0];'],['cx q[1],q[7];']]: savec(f'combo_q8_timing10_commute{j}',c,dict(family='compose',move='q8reuse+timing_q10q4_t10+commute_q1',variant=j,detail=d))
# reviewer corrected port + q8 reuse
rv=read(OUT/'review5_v25k')
rq=next(c for c,d in init_moves(rv) if d.get('move')=='reuse_mx' and d.get('q')==8)
savec('review5_q8',rq,dict(family='compose',move='reviewer_copy4+q8reuse'))
# q8 reviewer + timing candidate and q8 reviewer + commute candidates
rqt=next(c for c,d in timing_moves(rq,True) if d.get('op')==['cx q[10],q[4];'] and d.get('new')==10)
savec('review5_q8_timing10',rqt,dict(family='compose',move='reviewer_copy4+q8reuse+timing_q10q4_t10'))
for j,(c,d) in enumerate(commute_moves(rq)):
 if d.get('ops')==[['cx q[1],q[0];'],['cx q[1],q[7];']]: savec(f'review5_q8_commute{j}',c,dict(family='compose',move='reviewer_copy4+q8reuse+commute_q1',variant=j,detail=d))
print('done')
