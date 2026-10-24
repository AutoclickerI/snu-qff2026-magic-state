from core import *
import copy
from ortools.sat.python import cp_model

def commute(u,v):
 if not set(u['qs'])&set(v['qs']):return True
 if u['stmts'][0].startswith('cx ') and v['stmts'][0].startswith('cx '):
  c,t=u['qs'];d,s=v['qs'];return c!=s and d!=t
 return False

def build(cancel=True,reorder=False,tag='simplified',source=None):
 us,dets=parse_source() if source is None else (json.loads(Path(str(source)+'.units.json').read_text()),[s for s in Path(str(source)+'.qasm').read_text().splitlines() if s.startswith('// DETECTOR')]);pre=[u for u in us if u['region']=='pre'];prep=[u for u in us if u['region']=='prep'];rnd=[u for u in us if u['region']=='round'];removed=[];oldr=min(u['t'] for u in rnd)
 if cancel:
  changed=True
  while changed:
   changed=False
   for i,u in enumerate(prep):
    if not u['stmts'][0].startswith('cx '):continue
    for j in range(i+1,len(prep)):
     v=prep[j]
     if u['stmts']==v['stmts']:
      removed.append((u['qs'],u['t'],v['t']));prep.pop(j);prep.pop(i);changed=True;break
     if not commute(u,v):break
    if changed:break
 release={}
 for u in pre:
  for q in u['qs']:release[q]=max(release.get(q,0),u['t']+1)
 if reorder:
  m=cp_model.CpModel();ts=[m.NewIntVar(0,60,f't{i}') for i in range(len(prep))];ends=[t+1 for t in ts];ivs=[m.NewFixedSizeIntervalVar(t,1,f'o{i}') for i,t in enumerate(ts)]
  for q in range(36):m.AddNoOverlap([ivs[i] for i,u in enumerate(prep) if q in u['qs']])
  for i,u in enumerate(prep):
   m.Add(ts[i]>=max(release.get(q,0) for q in u['qs']))
   for j in range(i):
    if not commute(u,prep[j]):m.Add(ts[i]>=ts[j]+1)
  R=m.NewIntVar(33,60,'R')
  for t in ts:m.Add(R>=t+1)
  m.Minimize(R*10000-sum(ts));s=cp_model.CpSolver();s.parameters.num_workers=2;s.parameters.max_time_in_seconds=60;s.parameters.cp_model_presolve=False
  status=s.Solve(m);assert status in (cp_model.OPTIMAL,cp_model.FEASIBLE);r=s.Value(R)
  for u,t in zip(prep,ts):u['t']=s.Value(t)
  print('solver',s.StatusName(status),s.BestObjectiveBound(),flush=True)
 else:
  end=release.copy()
  for u in prep:
   st=max(end.get(q,0) for q in u['qs'])
   for q in u['qs']:end[q]=st+1
  r=max(end.values());late={q:r for q in range(36)}
  for u in reversed(prep):
   u['t']=min(late[q] for q in u['qs'])-1
   for q in u['qs']:late[q]=u['t']
 for u in rnd:u['t']+=r-oldr
 emit(pre+prep+rnd,dets,D,HERE/tag,dict(R=r,removed=removed))
 print(tag,'R',r,'removed',removed,flush=True)
if __name__=='__main__':
 build(True,False,'cancel_alap');build(False,True,'commute');build(True,True,'cancel_commute')
