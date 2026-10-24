"""Use live syndrome/guard helpers: two cancelling CXs, existing readout only."""
from v35_build import *
jobs=[]
for logical,path in PATHS.items():
 for q,a,z in path:
  for h in adjacent(q):
   if h in DATA:continue
   available=[t for t in range(max(30,a),min(43,z)+1)if not any(t==o['t']and(q in o['qs']or h in o['qs'])for o in BASE['ops'])]
   chunks=[]
   for t in available:
    if chunks and chunks[-1][-1]==t-1:chunks[-1].append(t)
    else:chunks.append([t])
   for chunk in chunks:
    if len(chunk)<2:continue
    for axis in ['Z','X']:
     first,last=chunk[0],chunk[-1];c=clone();edge=[h,q]if axis=='Z'else[q,h]
     add(c,'CX',edge,first);add(c,'CX',edge,last)
     name=f'live_{axis}_q{q}_h{h}_{first}_{last}'
     jobs.append(emit(name,c,dict(family='live_helper_existing_detector',gadget=dict(q=q,h=h,axis=axis,first=first,last=last,logical=logical),argument='Two CXs cancel ideally; data and helper have no intervening operation, so all intervening gates commute. Existing detectors price actual error sensitivity.')))
(V/'live_jobs.json').write_text(json.dumps(jobs,indent=2));print('LIVE',len(jobs))
