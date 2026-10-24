from round35 import *
from ortools.sat.python import cp_model
A=[1,14,8,9,2,16,15];src=ROOT/'work/lanes/MAIN/v35b';ops,dets,md=load(src);OUT=HERE/'r36'
init={1:38,14:38,8:36,9:38,2:38,16:41,15:40}
owned={i for i,o in enumerate(ops) if set(o.qs)<=set(A) and all(o.time>=init[q] for q in o.qs) and o.time<=43};oldbits={ops[i].bit for i in owned if ops[i].bit is not None}
keep=[copy.deepcopy(o) for i,o in enumerate(ops) if i not in owned]
# Freeze B/C resource schedule using its physical initialization boundary.
bc_start={6:41,26:32,13:25,11:33,4:36,23:32,27:32,12:37,25:33,19:33,17:32,5:35,29:32,28:32}
fixed=set()
for i,o in enumerate(keep):
 if o.time<16 or o.time>=43:fixed.add(i)
 if set(o.qs)<=set(bc_start) and all(o.time>=bc_start[q] for q in o.qs):fixed.add(i)
# Keep every source detector; source ends determine earliest A preparation.
boundbits={1:64,14:12,8:54,9:56,2:67,16:55,15:57}
bound={q:next(i for i,o in enumerate(keep) if o.bit==bit) for q,bit in boundbits.items()}
def commute(x,y):
 if not set(x.qs)&set(y.qs):return True
 if x.kind==y.kind=='CX':return x.qs[0]!=y.qs[1] and x.qs[1]!=y.qs[0]
 if y.kind=='CX':x,y=y,x
 if x.kind=='CX':
  if y.kind in ('T','TDG','S','SDG','Z','M'):return y.qs[0]==x.qs[0]
  if y.kind in ('MX','X','SX','SXDG'):return y.qs[0]==x.qs[1]
 if x.kind in ('T','TDG','S','SDG','Z','M') and y.kind in ('T','TDG','S','SDG','Z','M'):return True
 return False
m=cp_model.CpModel();tt=[m.NewIntVar(0,46,f't{i}') for i in range(len(keep))]
for i,o in enumerate(keep):
 m.AddHint(tt[i],o.time)
 if i in fixed:m.Add(tt[i]==o.time)
 else:m.Add(tt[i]>=16);m.Add(tt[i]<=min(o.time,42))
 for j,x in enumerate(keep[:i]):
  if not commute(x,o):m.Add(tt[i]>=tt[j]+1)
for q in range(36):m.AddAllDifferent([tt[i] for i,o in enumerate(keep) if q in o.qs])
# First earliest latest source, then total release, then smallest movement.
last=m.NewIntVar(0,42,'last');m.AddMaxEquality(last,[tt[i] for i in bound.values()]);m.Minimize(last*100000+sum(tt[i] for i in bound.values())*1000-sum(tt))
s=cp_model.CpSolver();s.parameters.num_workers=7;s.parameters.max_time_in_seconds=180;s.parameters.log_search_progress=True
st=s.Solve(m);out=dict(status=s.StatusName(st),seconds=s.WallTime(),bound=s.BestObjectiveBound())
if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):
 out.update(release={q:s.Value(tt[i]) for q,i in bound.items()},moves=[dict(index=i,kind=o.kind,qs=o.qs,old=o.time,new=s.Value(tt[i]),bit=o.bit) for i,o in enumerate(keep) if o.time!=s.Value(tt[i])])
 for i,o in enumerate(keep):o.time=s.Value(tt[i])
 # Store the prefix and frozen non-A resource, before a newly synthesized A0 round.
 out['ops']=[vars(o) for o in keep];out['dets']=[sorted(row) for row in dets if not row&oldbits];out['meta']=md;out['removed_prep_bits']=sorted(oldbits)
(OUT/'prefix_release.json').write_text(json.dumps(out,indent=2));print('RESULT',json.dumps({k:v for k,v in out.items() if k not in ('ops','dets','meta')}),flush=True)
