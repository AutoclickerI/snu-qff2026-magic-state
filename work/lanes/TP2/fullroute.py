"""Release-aware teleport routing. Native time steps, explicit 2-CX moves with reset.
All token initial cells are never-used prefix cells. C may be retired before
this window. Constraints on initial encoders are explicit model options.
"""
import os,sys,json,time,argparse
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from ortools.sat.python import cp_model
from packing import D,P,F,nb
EDGES=[(u,v) for u in range(36) for v in nb(u)]

def solve(a):
 started=time.monotonic();m=cp_model.CpModel();H=a.horizon;iv={q:[] for q in range(36)};tokens={}
 def V(lo,hi,n=''):return m.NewIntVar(lo,hi,n)
 def eq(x,q):
  z=m.NewBoolVar('');m.Add(x==q).OnlyEnforceIf(z);m.Add(x!=q).OnlyEnforceIf(z.Not());return z
 for k in 'obc':
  for i in range(7):
   n=a.hops
   pos=[V(0,35,f'{k}{i}p{j}') for j in range(n+1)]
   m.AddAllowedAssignments([pos[0]],[(q,) for q in sorted(F)])
   mv=[m.NewBoolVar(f'{k}{i}m{j}') for j in range(n)]
   ts=[V(33,H,f'{k}{i}t{j}') for j in range(n)]
   en=[V(33,H,f'{k}{i}e{j}') for j in range(n)]
   reset=[V(32,H,f'{k}{i}r{j}') for j in range(n)]
   for j in range(n):
    m.AddAllowedAssignments([pos[j],pos[j+1],mv[j]],[(u,v,1) for u,v in EDGES]+[(q,q,0) for q in range(36)])
    m.Add(en[j]==ts[j]+2*mv[j]);m.Add(reset[j]==ts[j]-mv[j])
    if j:m.Add(ts[j]>=en[j-1]);m.Add(mv[j]<=mv[j-1])
   tc=V(33,H-1,f'{k}{i}couple');last=V(34,H+1)
   if k=='o':m.Add(last==H+1)
   else:m.Add(last==tc+2);m.Add(tc>=en[-1])
   arrivals=[32]+reset;departures=en+[last];mem=[]
   for j in range(n+1):
    size=V(0,H+1-32);m.Add(size==departures[j]-arrivals[j]);bits=[]
    for q in range(36):
     z=eq(pos[j],q);bits.append(z);iv[q].append(m.NewOptionalIntervalVar(arrivals[j],size,departures[j],z,''))
    mem.append(bits)
   tokens[k,i]=dict(pos=pos,mv=mv,ts=ts,en=en,reset=reset,tc=tc,mem=mem)
 for q in P-set(D):iv[q].append(m.NewFixedSizeIntervalVar(32,1,''))
 for i,d in enumerate(D):
  o,b=(tokens[k,i] for k in 'ob')
  end=V(35,H+1);m.Add(end==o['tc']+2)
  sz=V(3,H-31);m.Add(sz==end-32);iv[d].append(m.NewIntervalVar(32,sz,end,''))
  at=V(0,35,f'o{i}atD');atb=V(0,35,f'o{i}atB');o['atD']=at;o['atB']=atb
  for when,where in ((o['tc'],at),(b['tc'],atb)):
   seg=[m.NewBoolVar('') for _ in o['pos']];m.AddExactlyOne(seg)
   for j,z in enumerate(seg):
    m.Add(where==o['pos'][j]).OnlyEnforceIf(z)
    if j:m.Add(when>=o['en'][j-1]).OnlyEnforceIf(z)
    if j<len(o['ts']):m.Add(when<o['ts'][j]).OnlyEnforceIf(z)
  m.AddAllowedAssignments([at],[(q,) for q in nb(d)])
  m.AddAllowedAssignments([atb,b['pos'][-1]],EDGES)
  m.Add(b['tc']>=o['tc']+1)
  m.Add(b['tc']>=o['en'][-1])
  c=tokens['c',i]
  bv=V(0,35,f'b{i}atC');b['atC']=bv
  seg=[m.NewBoolVar('') for _ in b['pos']];m.AddExactlyOne(seg)
  for j,z in enumerate(seg):
   m.Add(bv==b['pos'][j]).OnlyEnforceIf(z)
   if j:m.Add(c['tc']>=b['en'][j-1]).OnlyEnforceIf(z)
   if j<len(b['ts']):m.Add(c['tc']<b['ts'][j]).OnlyEnforceIf(z)
  m.AddAllowedAssignments([bv,c['pos'][-1]],EDGES)
  m.Add(b['tc']>=c['tc']+1)
  m.Add(b['tc']<=c['tc']+a.vgap)
  if not a.postmove:
   m.Add(o['tc']>=o['en'][-1]);m.Add(at==o['pos'][-1])
 for q in range(36):m.AddNoOverlap(iv[q])
 # Initial block connectivity, zero helpers (sufficient for exact encoders).
 if a.connect=='both':
  parts=json.loads(Path(__file__).with_name('three_partitions.json').read_text())
  memvars=[]
  for k in 'obc':
   for q in sorted(F):
    z=m.NewBoolVar('member');m.Add(z==sum(tokens[k,i]['mem'][0][q] for i in range(7)));memvars.append(z)
  m.AddAllowedAssignments(memvars,[[int(q in p[j]) for j in range(3) for q in sorted(F)] for p in parts])
 for k in ('o' if a.connect=='o' else ''):
  mem={q:sum(tokens[k,i]['mem'][0][q] for i in range(7)) for q in F}
  fl={(u,v):V(0,7) for u,v in EDGES if u in F and v in F}
  for (u,v),z in fl.items():m.Add(z<=7*mem[u]);m.Add(z<=7*mem[v])
  for q in F:m.Add(sum(fl[q,v]-fl[v,q] for v in nb(q) if (q,v) in fl)==7*tokens[k,0]['mem'][0][q]-mem[q])
 cpos=[]
 if a.joint:
  cpos=[V(0,35,f'c{i}') for i in range(7)]
  for i,x in enumerate(cpos):
   m.AddAllowedAssignments([x],[(q,) for q in F]);m.AddAllowedAssignments([tokens['b',i]['pos'][0],x],EDGES)
  m.AddAllDifferent([tokens[k,i]['pos'][0] for k in 'ob' for i in range(7)]+cpos)
  mem={q:1-sum(tokens['o',i]['mem'][0][q] for i in range(7)) for q in F}
  fl={(u,v):V(0,14) for u,v in EDGES if u in F and v in F}
  for (u,v),z in fl.items():m.Add(z<=14*mem[u]);m.Add(z<=14*mem[v])
  for q in F:m.Add(sum(fl[q,v]-fl[v,q] for v in nb(q) if (q,v) in fl)==14*tokens['b',0]['mem'][0][q]-mem[q])
 if a.fixed:
  fixed=json.loads(Path(a.fixed).read_text())
  for k in 'obc':
   if k not in fixed:continue
   for i,q in enumerate(fixed[k]):m.Add(tokens[k,i]['pos'][0]==q)
 last=V(34,H-1,'last_cx');m.AddMaxEquality(last,[v['tc'] for (k,i),v in tokens.items() if k=='b'])
 moves=sum(x for v in tokens.values() for x in v['mv'])
 gaps=sum(tokens['b',i]['tc']-tokens['c',i]['tc'] for i in range(7))
 m.Minimize(1000000*last+1000*moves+100*gaps+sum(tokens['b',i]['tc']-tokens['o',i]['tc'] for i in range(7)))
 if a.hint:
  h=json.loads(Path(a.hint).read_text())
  for key,t in h.get('tokens',{}).items():
   v=tokens[key[0],int(key[1:])]
   for name in ('pos','ts','en'):
    for x,z in zip(v[name],t[name]):m.AddHint(x,z)
   m.AddHint(v['tc'],t['tc'])
 if a.first:m.ClearObjective()
 s=cp_model.CpSolver();s.parameters.max_time_in_seconds=a.seconds;s.parameters.num_workers=a.workers;s.parameters.random_seed=a.seed;s.parameters.cp_model_presolve=not a.no_presolve
 if a.first:s.parameters.stop_after_first_solution=True;s.parameters.linearization_level=0
 class CB(cp_model.CpSolverSolutionCallback):
  def on_solution_callback(self):print('solution',self.ObjectiveValue(),self.BestObjectiveBound(),self.WallTime(),flush=True)
 status=s.Solve(m,CB());out=dict(args=vars(a),status=s.StatusName(status),wall=time.monotonic()-started,stats=s.ResponseStats())
 if status in (cp_model.OPTIMAL,cp_model.FEASIBLE):
  out.update(last_cx=s.Value(last),R=min(s.Value(tokens['o',i]['tc']) for i in range(7)),Rmax=max(s.Value(tokens['o',i]['tc']) for i in range(7)),moves=s.Value(moves),tokens={f'{k}{i}':{key:([s.Value(x) for x in val] if isinstance(val,list) else s.Value(val)) for key,val in v.items() if key!='mem'} for (k,i),v in tokens.items()})
  for k in 'obc':out[k]=[s.Value(tokens[k,i]['pos'][0]) for i in range(7)]
 Path(a.out).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ('tokens','stats')}),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--horizon',type=int,default=46);p.add_argument('--hops',type=int,default=4);p.add_argument('--workers',type=int,default=6);p.add_argument('--seconds',type=float,default=180);p.add_argument('--seed',type=int,default=0);p.add_argument('--connect',choices=['none','o','both'],default='both');p.add_argument('--postmove',action='store_true');p.add_argument('--joint',action='store_true');p.add_argument('--no-presolve',action='store_true');p.add_argument('--hint');p.add_argument('--fixed');p.add_argument('--vgap',type=int,default=3);p.add_argument('--first',action='store_true');solve(p.parse_args())
