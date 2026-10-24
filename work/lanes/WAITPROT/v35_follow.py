"""Additional complete bundles and explicit repairs of helper-basis failures."""
from v35_build import *
from v35_publish import circuit

jobs=[]
def put(name,c,description):
 r=emit(name,c,description);r['procs']=4;jobs.append(r)
def fund(c):
 find(c,t=13,qs=[19],kind='R')['t']=17;find(c,t=25,qs=[13],kind='R')['t']=33;return c
def release(c):return gadget(c,dict(q=7,h=13,axis='Z',init=26,first=27,last=31,end=32,restore=None))
new05=dict(q=20,h=21,axis='X',init=33,first=34,last=35,end=36,restore=None)
for name in ['new_04_Z_q20_h21','new_08_Z_q10_h16','new_16_Z_q15_h16']:
 g=json.loads((V/(name+'.json')).read_text())['description']['gadget'];g=copy.deepcopy(g)
 # End in |0> before the next data-transfer CX. Shorten only when the reset
 # cannot fit otherwise; preserve the failed original as evidence.
 g['last']=min(g['last'],g['free'][1]-2);g['end']=g['last']+1;g['restore']=g['last']+2
 if g['last']<=g['first']:
  (V/(name+'.repair.json')).write_text(json.dumps(dict(feasible=False,reason='Four free ticks cannot fit reset+two CX+MX+Z-basis restoration.',gadget=g),indent=2));continue
 put('repair_'+name,gadget(clone(),g),dict(family='restored_helper_basis',gadget=g,repairs=name))
c=clone();find(c,t=25,qs=[13],kind='R')['t']=33
put('follow_released7Z_new05',gadget(release(c),new05),dict(family='combination',ingredients=['released q7 Z','new05']))
put('follow_fund_released7Z_new05',gadget(release(fund(clone())),new05),dict(family='combination',ingredients=['late_resets_joint','released q7 Z','new05']))
source=ROOT/'work/lanes/ST2/v35/tightened/restore_181_182_188_40'
for released in [False,True]:
 c=fund(circuit(source))
 if released:release(c)
 gadget(c,new05)
 name='follow_st2best_fund_new05'+('_released7Z'if released else'')
 put(name,clone(c),dict(family='combination',ingredients=['ST2 best','late_resets_joint','new05']+(['released q7 Z']if released else[])))
 for first,last in [(19,28),(21,28)]:
  d=clone(c)
  if first==19:find(d,t=19,qs=[21],kind='R')['t']=18
  add(d,'CX',[20,21],first);add(d,'CX',[20,21],last)
  put(name+f'_share{first}_{last}',d,dict(family='combination',ingredients=['ST2 best','late_resets_joint','new05','released q7 Z'if released else'no release',f'share existing q15 helper with q20 at{first}/{last}']))
# Explicit Fano-line coverage: shared Z guard on0/7 plus existing Z20 in ST2.
for q,h,axis,first,last in [(7,6,'Z',36,38),(3,4,'Z',41,43),(3,9,'X',39,42),(10,4,'Z',38,39)]:
 c=gadget(release(fund(circuit(source))),new05);edge=[h,q]if axis=='Z'else[q,h]
 add(c,'CX',edge,first);add(c,'CX',edge,last)
 put(f'follow_st2best_live_{axis}_{q}_{h}',c,dict(family='combination',ingredients=['ST2 best','funding','released q7 Z','new05',f'live {axis} q{q}/h{h} {first}/{last}']))
(V/'follow_jobs.json').write_text(json.dumps(jobs,indent=2));print('FOLLOW',len(jobs))
