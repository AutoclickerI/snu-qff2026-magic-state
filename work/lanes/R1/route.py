"""Time-expanded token routing, native steps 33..H.
Two-CX block moves; data and B get a destination reset (3 steps).
A uses measured known-|m> targets and carries X-frame records into A detectors.
C is assumed consumed before t=33: a relaxed phased-preparation geometry.
Each data token moves before its A coupling; A/B may move independently.
The occupancy intervals reserve both cells throughout every physical transfer.
"""
import os,sys,json,argparse,time
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from ortools.sat.python import cp_model
from pathlib import Path
P0={0,1,2,3,4,6,7,8,9,10,13,14,15,19,20}
D0=[0,20,7,4,3,15,8]
def nb(q):
 r,c=divmod(q,6)
 return [rr*6+cc for rr,cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=rr<6 and 0<=cc<6]
EDGES=[(u,v) for u in range(36) for v in nb(u)]
def transform(k,tr,tc):
 def f(q):
  r,c=divmod(q,6)
  return [(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][k]
 rr=min(f(q)[0] for q in P0);cc=min(f(q)[1] for q in P0)
 mp=lambda q:(f(q)[0]-rr+tr)*6+f(q)[1]-cc+tc
 return set(map(mp,P0)),list(map(mp,D0))

def solve(a):
 started=time.monotonic();P,D=transform(*map(int,a.transform.split(',')));F=sorted(set(range(36))-P)
 components=[];left=set(F)
 while left:
  cc={min(left)}
  for _ in F:cc|={v for u in cc for v in nb(u) if v in F}
  components.append(sorted(cc));left-=cc
 good=set(q for cc in components if len(cc)>=7 for q in cc) if a.prep_components else set(F)
 m=cp_model.CpModel();H=a.horizon;iv={q:[] for q in range(36)};tokens={};starts={};end=[]
 def V(lo,hi,n):return m.NewIntVar(lo,hi,n)
 def eq(x,q):
  z=m.NewBoolVar('');m.Add(x==q).OnlyEnforceIf(z);m.Add(x!=q).OnlyEnforceIf(z.Not());return z
 for k in 'dab':
  for i in range(7):
   n=a.dhops if k=='d' else a.bhops
   pos=[V(0,35,f'{k}{i}p{j}') for j in range(n+1)]
   if k=='d':m.Add(pos[0]==D[i])
   else:m.AddAllowedAssignments([pos[0]],[(q,) for q in sorted(good)])
   starts[k,i]=pos[0]
   mv=[m.NewBoolVar(f'{k}{i}m{j}') for j in range(n)]
   ts=[V(33,H,f'{k}{i}t{j}') for j in range(n)]
   duration=2 if (k=='a' and not a.reset_a) or (k=='b' and a.fast_b) else 3
   en=[V(33,H,f'{k}{i}e{j}') for j in range(n)]
   target_start=[V(32,H,f'{k}{i}r{j}') for j in range(n)]
   fast=[m.NewBoolVar(f'{k}{i}fast{j}') for j in range(n)]
   for j in range(n):
    m.AddAllowedAssignments([pos[j],pos[j+1],mv[j]],[(u,v,1) for u,v in EDGES]+[(q,q,0) for q in range(36)])
    if a.physical:
     m.Add(en[j]==ts[j]+2*mv[j]);m.Add(target_start[j]==ts[j]-mv[j]+fast[j]);m.Add(fast[j]<=mv[j])
     # Only the initial prefix measurement can justify an unreset known frame.
     if j or k=='d':m.Add(fast[j]==0)
     else:
      # q19's transformed index is the unique Z measurement; the remaining released sites are MX.
      kk,rr,cc=map(int,a.transform.split(','))
      def tfq(q):
       r,c=divmod(q,6);return [(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][kk]
      r0=min(tfq(q)[0] for q in P0);c0=min(tfq(q)[1] for q in P0)
      zq=(tfq(19)[0]-r0+rr)*6+tfq(19)[1]-c0+cc
      fastcells=sorted(P-set(D)-{zq}) if k=='b' else [zq]
      m.AddAllowedAssignments([pos[j+1]],[(q,) for q in fastcells]).OnlyEnforceIf(fast[j]);m.Add(ts[j]==33).OnlyEnforceIf(fast[j])
    else:
     m.Add(en[j]==ts[j]+duration*mv[j]);m.Add(target_start[j]==ts[j]);m.Add(fast[j]==0)
    m.Add(ts[j]>=33 if j==0 else ts[j]>=en[j-1])
    if j:m.Add(mv[j]<=mv[j-1])
   ready=en[-1] if n else 33
   coupling=V(33,H-1,f'{k}{i}couple')
   if k!='d' or not a.interleaved:m.Add(coupling>=ready)
   last=V(34,H+1,f'{k}{i}last')
   if k=='d':m.Add(last==H+1)
   else:m.Add(last==coupling+2)
   arrivals=[32 if a.physical and k!='d' else 33]+target_start
   departures=en+[last]
   mem=[]
   for j in range(n+1):
    size=V(0,H+1-32,f'{k}{i}s{j}');m.Add(size==departures[j]-arrivals[j]);bits=[]
    for q in range(36):
     z=eq(pos[j],q);bits.append(z);iv[q].append(m.NewOptionalIntervalVar(arrivals[j],size,departures[j],z,''))
    mem.append(bits)
   tokens[k,i]=dict(pos=pos,mv=mv,ts=ts,en=en,coupling=coupling,mem=mem,target_start=target_start,fast=fast)
 if a.physical:
  for q in P:iv[q].append(m.NewFixedSizeIntervalVar(32,1,''))
 for q in range(36):m.AddNoOverlap(iv[q])
 for i in range(7):
  d,aa,b=(tokens[k,i] for k in 'dab')
  atA=V(0,35,f'd{i}atA');d['atA']=atA
  if a.interleaved:
   seg=[m.NewBoolVar('') for _ in d['pos']];m.AddExactlyOne(seg)
   for j,z in enumerate(seg):
    m.Add(atA==d['pos'][j]).OnlyEnforceIf(z)
    if j:m.Add(d['coupling']>=d['en'][j-1]).OnlyEnforceIf(z)
    if j<len(d['ts']):m.Add(d['coupling']<d['ts'][j]).OnlyEnforceIf(z)
   m.Add(b['coupling']>=d['en'][-1] if d['en'] else b['coupling']>=33)
  else:m.Add(atA==d['pos'][-1])
  m.AddAllowedAssignments([atA,aa['pos'][-1]],EDGES)
  m.AddAllowedAssignments([d['pos'][-1],b['pos'][-1]],EDGES)
  m.Add(d['coupling']==aa['coupling']);m.Add(b['coupling']>=aa['coupling']+1)
  # Data cannot be measured, and all movement is before A then B.
  end.append(b['coupling'])
 if a.synchronous:
  for i in range(1,7):m.Add(tokens['a',i]['coupling']==tokens['a',0]['coupling']);m.Add(tokens['b',i]['coupling']==tokens['b',0]['coupling'])
 # Every B must have an unused partner C in F for its prior transversal verification.
 cpos=[V(0,35,f'c{i}') for i in range(7)]
 if a.verify:
  for i in range(7):
   m.AddAllowedAssignments([cpos[i]],[(q,) for q in F]);m.AddAllowedAssignments([starts['b',i],cpos[i]],EDGES)
  m.AddAllDifferent([starts['b',i] for i in range(7)]+cpos)
 if a.stageabc:
  m.AddAllDifferent([starts[k,i] for k in 'ab' for i in range(7)]+cpos)
  bmem={q:1-sum(tokens['a',i]['mem'][0][q] for i in range(7)) for q in F}
  fl={(u,v):V(0,14,'') for u,v in EDGES if u in F and v in F}
  for (u,v),z in fl.items():m.Add(z<=14*bmem[u]);m.Add(z<=14*bmem[v])
  for q in F:m.Add(sum(fl[q,v]-fl[v,q] for v in nb(q) if (q,v) in fl)==14*tokens['b',0]['mem'][0][q]-bmem[q])
 # Connectivity for initial A on F\\B, with optionally <=helpers spare cells.
 if a.connect:
  bm={q:sum(tokens['b',i]['mem'][0][q] for i in range(7)) for q in F}
  am={q:sum(tokens['a',i]['mem'][0][q] for i in range(7)) for q in F}
  mem={q:m.NewBoolVar(f'am{q}') for q in F}
  for q in F:m.Add(mem[q]>=am[q]);m.Add(mem[q]+bm[q]<=1)
  m.Add(sum(mem.values())<=7+a.helpers)
  # Root A0: commodity units to each A site; arbitrary helper membership.
  flow={(u,v):V(0,7,'') for u,v in EDGES if u in F and v in F}
  for (u,v),z in flow.items():m.Add(z<=7*mem[u]);m.Add(z<=7*mem[v])
  for q in F:m.Add(sum(flow[q,v]-flow[v,q] for v in nb(q) if (q,v) in flow)==7*tokens['a',0]['mem'][0][q]-am[q])
 last=V(33,H,'last_round_cx');m.AddMaxEquality(last,end)
 dm=sum(v for (k,i),d in tokens.items() if k=='d' for v in d['mv'])
 bms=sum(v for (k,i),d in tokens.items() if k!='d' for v in d['mv'])
 m.Minimize(last*1000000+dm*10000+bms*100-sum(tokens[k,i]['coupling'] for k in 'ab' for i in range(7)) if a.alap else last*100000+dm*1000+bms*10+sum(end))
 if a.hint:
  h=json.loads(Path(a.hint).read_text())
  for key,d in h.get('tokens',{}).items():
   k=key[0];i=int(key[1:]);v=tokens[k,i]
   for x,z in zip(v['pos'],d['pos']):m.AddHint(x,z)
   for x,z in zip(v['ts'],d['times']):m.AddHint(x,z)
   m.AddHint(v['coupling'],d['coupling'])
 if a.fixed_paths:
  f=json.loads(Path(a.fixed_paths).read_text())
  if a.verify:
   for x,q in zip(cpos,f['c']):m.Add(x==q)
  for key,v in f['tokens'].items():
   for x,q in zip(tokens[key[0],int(key[1:])]['pos'],v['pos']):m.Add(x==q)
 if a.fixed:
  f=json.loads(Path(a.fixed).read_text())
  for k in 'ab':
   for i,q in enumerate(f[k]):m.Add(starts[k,i]==q)
 s=cp_model.CpSolver();s.parameters.max_time_in_seconds=a.seconds;s.parameters.num_workers=a.workers;s.parameters.random_seed=a.seed;s.parameters.cp_model_presolve=not a.no_presolve
 s.parameters.log_search_progress=a.log
 class CB(cp_model.CpSolverSolutionCallback):
  def on_solution_callback(self):print('incumbent',self.ObjectiveValue(),self.BestObjectiveBound(),self.WallTime(),flush=True)
 st=s.Solve(m,CB());out=dict(args=vars(a),status=s.StatusName(st),wall=time.monotonic()-started,stats=s.ResponseStats(),free_components=components,P=sorted(P),F=F,pre_data=D)
 if st in (cp_model.OPTIMAL,cp_model.FEASIBLE):
  out.update(last_cx=s.Value(last),R=min(s.Value(tokens['a',i]['coupling']) for i in range(7)),Rmax=max(s.Value(tokens['a',i]['coupling']) for i in range(7)),data_moves=s.Value(dm),block_moves=s.Value(bms),tokens={f'{k}{i}':dict(pos=[s.Value(p) for p in v['pos']],times=[s.Value(t) for t in v['ts']],ends=[s.Value(e) for e in v['en']],coupling=s.Value(v['coupling']),target_start=[s.Value(x) for x in v['target_start']],fast=[s.Value(x) for x in v['fast']]) for (k,i),v in tokens.items()})
  out['data_at_A']=[s.Value(tokens['d',i]['atA']) for i in range(7)]
  out.update(a=[s.Value(starts['a',i]) for i in range(7)],b=[s.Value(starts['b',i]) for i in range(7)],c=[s.Value(v) for v in cpos] if a.verify else [])
 Path(a.out).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ('tokens','stats')}),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--horizon',type=int,default=41);p.add_argument('--transform',default='0,0,0');p.add_argument('--dhops',type=int,default=2);p.add_argument('--bhops',type=int,default=3);p.add_argument('--workers',type=int,default=6);p.add_argument('--seconds',type=float,default=180);p.add_argument('--seed',type=int,default=0);p.add_argument('--connect',action='store_true');p.add_argument('--stageabc',action='store_true');p.add_argument('--helpers',type=int,default=7);p.add_argument('--verify',action='store_true');p.add_argument('--synchronous',action='store_true');p.add_argument('--reset-a',action='store_true');p.add_argument('--physical',action='store_true');p.add_argument('--prep-components',action='store_true');p.add_argument('--interleaved',action='store_true');p.add_argument('--fast-b',action='store_true');p.add_argument('--no-presolve',action='store_true');p.add_argument('--log',action='store_true');p.add_argument('--hint');p.add_argument('--fixed');p.add_argument('--fixed-paths');p.add_argument('--alap',action='store_true');solve(p.parse_args())
