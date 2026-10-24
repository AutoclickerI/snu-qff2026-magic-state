"""Separate storage detection from a refreshed future-data initialization."""
from v35_build import *
jobs=[]
def put(name,c,desc):
 r=emit(name,c,desc);r['procs']=2;jobs.append(r)
for end in [34,35,36]:
 c=clone();bit=nb(c);add(c,'R',[21],33);add(c,'M',[21],end,bit);c['dets'].append([bit])
 put(f'ablate_q21_refresh_m{end}',c,dict(family='helper_refresh_ablation',q=21,reset=33,measurement=end,comparison='new_05_X_q20_h21 without both CXs'))
for which in ['reset','measurement']:
 c=clone()
 if which=='reset':add(c,'R',[21],36)
 else:
  bit=nb(c);add(c,'M',[21],36,bit);c['dets'].append([bit])
 put('ablate_q21_'+which+'36',c,dict(family='helper_refresh_ablation',q=21,operation=which,t=36))
g=dict(q=20,h=21,axis='X',init=33,first=34,last=35,end=36,restore=None)
c=gadget(clone(),g);bit=nb(c)-1;c['dets'].remove([bit])
put('ablate_new05_no_detector',c,dict(family='guard_detector_ablation',source='new_05_X_q20_h21'))
(V/'mechanism_jobs.json').write_text(json.dumps(jobs,indent=2));print('MECHANISMS',len(jobs))
