"""Fix paths and order, minimize end, then shorten check-to-output exposure.
Orders remain those of the audited route. Preparations are regenerated ALAP.
"""
import os,sys,json
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from ortools.sat.python import cp_model
from packing import D,P
r=json.loads(Path(sys.argv[1]).read_text());m=cp_model.CpModel();tokens=r['tokens'];H=49
# Native jobs with the exact original per-cell order.
jobs=[]
def add(t,qs,name,ref):jobs.append(dict(t=t,qs=qs,name=name,ref=ref,s=m.NewIntVar(32,H,name)))
for key,v in tokens.items():
 for j,yes in enumerate(v['mv']):
  if not yes:continue
  u,w=v['pos'][j:j+2];t=v['ts'][j]
  add(t-1,[w],key+'.reset'+str(j),(key,j,'reset'));add(t,[u,w],key+'.m1'+str(j),(key,j,'m1'));add(t+1,[u,w],key+'.m2'+str(j),(key,j,'m2'))
for i,q in enumerate(D):
 o,b=(tokens[f'{k}{i}'] for k in 'ob')
 add(o['tc'],[q,o['atD']],f'o{i}.cx',(f'o{i}',0,'cx'));add(o['tc']+1,[q],f'd{i}.m',(f'd{i}',0,'m'))
 add(b['tc'],[b['pos'][-1],o['atB']],f'b{i}.cx',(f'b{i}',0,'cx'));add(b['tc']+1,[b['pos'][-1]],f'b{i}.m',(f'b{i}',0,'m'))
J={x['ref']:x['s'] for x in jobs}
for q in range(36):
 js=sorted([x for x in jobs if q in x['qs']],key=lambda x:x['t'])
 for a,b in zip(js,js[1:]):m.Add(b['s']>=a['s']+1)
 for x in js:
  if q in P:m.Add(x['s']>=33)
for key,v in tokens.items():
 active=[j for j,x in enumerate(v['mv']) if x]
 for j in active:
  m.Add(J[key,j,'m1']==J[key,j,'reset']+1);m.Add(J[key,j,'m2']==J[key,j,'m1']+1)
 # Reservations while waiting preserve original order, and no gaps inside a move.
 for j,k in zip(active,active[1:]):m.Add(J[key,k,'m1']>=J[key,j,'m2']+1)
for i in range(7):
 m.Add(J[f'd{i}',0,'m']==J[f'o{i}',0,'cx']+1)
 m.Add(J[f'b{i}',0,'m']==J[f'b{i}',0,'cx']+1)
 m.Add(J[f'b{i}',0,'cx']>=J[f'o{i}',0,'cx']+1)
end=m.NewIntVar(33,H,'end');m.AddMaxEquality(end,[x['s'] for x in jobs]);m.Minimize(end)
s=cp_model.CpSolver();s.parameters.num_workers=2;s.parameters.max_time_in_seconds=30
st=s.Solve(m);assert st in (cp_model.OPTIMAL,cp_model.FEASIBLE);best=s.Value(end)
m.Add(end==best);m.Minimize(sum(J[f'b{i}',0,'cx']-J[f'o{i}',0,'cx'] for i in range(7))*10000-sum(x['s'] for x in jobs))
st=s.Solve(m);assert st in (cp_model.OPTIMAL,cp_model.FEASIBLE)
for key,v in tokens.items():
 for j,yes in enumerate(v['mv']):
  if yes:v['ts'][j]=s.Value(J[key,j,'m1']);v['en'][j]=v['ts'][j]+2;v['reset'][j]=v['ts'][j]-1
 last=max([v['en'][j] for j,yes in enumerate(v['mv']) if yes]+[33])
 for j,yes in enumerate(v['mv']):
  if not yes:v['ts'][j]=last;v['en'][j]=last;v['reset'][j]=last
 v['tc']=s.Value(J[key,0,'cx'])
r.update(R=min(tokens[f'o{i}']['tc'] for i in range(7)),Rmax=max(tokens[f'o{i}']['tc'] for i in range(7)),last_cx=max(tokens[f'b{i}']['tc'] for i in range(7)),alap_status=s.StatusName(st),alap_stats=s.ResponseStats())
Path(sys.argv[2]).write_text(json.dumps(r,indent=2)+'\n');print('ALAP',r['R'],r['Rmax'],r['last_cx'],s.StatusName(st))
