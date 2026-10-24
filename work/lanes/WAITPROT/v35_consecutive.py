"""Consecutive CX identities: one orientation suffices for isotropic 2q noise."""
from v35_build import *
jobs=[];seen=set()
for logical,path in PATHS.items():
 for q,a,z in path:
  for h in adjacent(q):
   if h in DATA:continue
   for first in range(max(30,a),min(43,z)):
    last=first+1
    if any(o['t']in(first,last)and(q in o['qs']or h in o['qs'])for o in BASE['ops']):continue
    if(q,h,first,last)in seen:continue
    seen.add((q,h,first,last))
    existing=V/f'live_X_q{q}_h{h}_{first}_{last}.json'
    if existing.exists():continue
    c=clone();add(c,'CX',[q,h],first);add(c,'CX',[q,h],last)
    r=emit(f'cxpair_q{q}_h{h}_{first}_{last}',c,dict(family='consecutive_cx_identity',q=q,h=h,first=first,last=last,logical=logical,orientation_equivalence='CX; depolarize2; CX; depolarize2 equals two isotropic depolarize2 channels; reversing CX direction leaves the channel unchanged.'))
    r['procs']=2;jobs.append(r)
(V/'consecutive_jobs.json').write_text(json.dumps(jobs,indent=2));print('CONSECUTIVE',len(jobs),'total windows',len(seen))
