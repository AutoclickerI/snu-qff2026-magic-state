import sys,copy,json,re,collections
from pathlib import Path
sys.path.insert(0,'work/lanes/FRESH');import common
from ortools.sat.python import cp_model
H=Path('work/lanes/FRESH')

def build(stem,name,seconds=60):
 c=common.read(stem);ops=c['ops'];
 ladder=json.load(open('work/lanes/SEPBC/inputs/ladder_f00.json'))['units'];pref=[tuple(x['lines']) for x in ladder if x.get('tag')=='prefix']
 order=sorted(range(len(ops)),key=lambda i:(ops[i]['t'],i));lines=[tuple(ops[i]['lines']) for i in order]
 pi=[];j=0
 for k,i in enumerate(order):
  if j<len(pref) and tuple(ops[i]['lines'])==pref[j]:pi.append(i);j+=1
 assert j==len(pref),(j,len(pref));ps=set(pi)
 # Native operations originally at/after R are final round/hops/readout; all other non-prefix operations are prep.
 R0=int(c['meta']['R']);rounds={i for i in range(len(ops)) if i not in ps and ops[i]['t']>=R0};preps=set(range(len(ops)))-ps-rounds
 print('class',len(ps),len(preps),len(rounds),'R0',R0)
 m=cp_model.CpModel();R=m.NewIntVar(33,R0,'R');tv=[m.NewIntVar(0,100,f't{i}') for i in range(len(ops))]
 for i,o in enumerate(ops):
  if i in ps:m.Add(tv[i]==o['t'])
  elif i in rounds:m.Add(tv[i]==R+o['t']-R0)
  else:m.Add(tv[i]<R)
 # Per-wire native order as emitted.
 by=collections.defaultdict(list)
 for i in order:
  for q in common.unit(ops[i]).qs:by[q].append(i)
 for seq in by.values():
  for a,b in zip(seq,seq[1:]):m.Add(tv[b]>tv[a])
 m.Minimize(R);s=cp_model.CpSolver();s.parameters.max_time_in_seconds=seconds;s.parameters.num_search_workers=1;st=s.Solve(m);print('solve',s.StatusName(st),s.WallTime())
 if st not in (cp_model.FEASIBLE,cp_model.OPTIMAL):return
 best=s.Value(R);m.Add(R==best);m.Maximize(sum(tv[i] for i in preps));st=s.Solve(m);print('tie',s.StatusName(st),s.WallTime(),best)
 for i,o in enumerate(ops):o['t']=s.Value(tv[i]);o['id']=i
 c['meta']['R']=best;c['meta']['early_retime']=dict(prefix=len(ps),prep=len(preps),round=len(rounds),solver=s.StatusName(st),R=best)
 out=common.save(c,name);print(out,common.score(out));return out
if __name__=='__main__':build(sys.argv[1],sys.argv[2])
