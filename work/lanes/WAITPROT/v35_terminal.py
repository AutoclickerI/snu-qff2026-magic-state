"""Combine the final two independent positive additions and close axis variants."""
from v35_build import *
from v35_publish import circuit
source=circuit(V/'close_ABCDEF_postT0');jobs=[]
def put(name,c,**desc):
 r=emit(name,c,dict(family='combination',**desc));r['procs']=4;jobs.append(r)
for t in [30,31]:add(source,'CX',[4,10],t)
put('terminal_joint',clone(source),source='close_ABCDEF_postT0',added_pair=[4,10,30,31])
# Consecutive X/Z orientations are equal locally; keep one representative.
# q7 has one unprotected late window whose existing helper is live. Full
# maximal-window runs were negative; test one funded pair before declaring it.
for q,h,first,last in [(22,16,42,43),(7,6,36,37),(3,4,41,42)]:
 c=clone(source)
 # q0/h6 already consumes36/37; the replacement pays its actual cost.
 if h==6:
  c['ops']=[o for o in c['ops']if not(o['kind']=='CX'and o['qs']==[0,6]and o['t']in(36,37))]
 for t in [first,last]:add(c,'CX',[q,h],t)
 put(f'terminal_trade_{q}_{h}',c,source='terminal_joint',addition=[q,h,first,last],replaces_q0_pair=h==6)
(V/'terminal_jobs.json').write_text(json.dumps(jobs,indent=2));print('TERMINAL',len(jobs))
