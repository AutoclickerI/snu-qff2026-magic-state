"""Incremental reverse-endpoint SAT with shared backwards fault signatures.
All mutations and receipts stay below this lane. No solver timeout is UNSAT.
"""
import os, sys
sys.dont_write_bytecode = True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import argparse, itertools, json, random, time
from pathlib import Path
from pysat.solvers import Solver
from pysat.card import CardEnc, EncType
import stim
import ft_mb as ft
B,C,ROWS=ft.B,ft.C,ft.ROWS
HERE=Path(__file__).resolve().parent

def nb(q):
 r,c=divmod(q,6)
 return [u for u in (q-6 if r else -1,q+6 if r<5 else -1,q-1 if c else -1,q+1 if c<5 else -1) if u>=0]

def target(cells):
 return {q:sum(1<<(3*j+k) for j,blk in enumerate((B,C)) for k,row in enumerate(ROWS) if q in {blk[i] for i in row}) for q in cells}

def basis(seed):
 # Fix an explicit target basis instead of the forward model's arbitrary GL(6)
 # variables. Independent GL(3,2) code automorphisms diversify equivalent bases.
 r=random.Random(seed); blocks=[]
 for _ in range(2):
  a=[1,2,4]
  for i in range(20):
   u,v=r.sample(range(3),2);a[u]^=a[v]
  blocks.append(a)
 return blocks

def transform(v,bas):
 return sum(((v>>(3*j)&7 & a).bit_count()%2)<<(3*j+k) for j,aa in enumerate(bas) for k,a in enumerate(aa))

def verify(d):
 cells=d.get('cells',sorted(set(B+C+d['pivots'])|{q for l in d['ops'] for e in l for q in e}))
 c=stim.Circuit()
 for q in cells:c.append('R',[q])
 for q in d['pivots']:c.append('H',[q])
 sim=stim.TableauSimulator();sim.do(c)
 for ti,l in enumerate(d['ops']):
  used=set()
  for u,v in l:
   assert v in nb(u) and u not in used and v not in used
   used|={u,v};sim.cx(u,v)
  for q in d.get('measures',[[]for _ in d['ops']])[ti]:
   assert q not in used
   sim.postselect_x(q,desired_value=False);sim.reset(q)
 helpers=[q for q in cells if q not in B+C]
 if d.get('helper_x'):
  for q in helpers:sim.postselect_x(q,desired_value=False)
 vals=[]
 for blk in (B,C):
  for pauli,row in [('X',r) for r in ROWS]+[('Z',r) for r in ROWS]+[('Z',list(range(7)))]:
   p=stim.PauliString(max(cells)+1)
   for i in row:p[blk[i]]=pauli
   vals.append(sim.peek_observable_expectation(p))
 if not d.get('helper_x'):
  for q in helpers:
   p=stim.PauliString(max(cells)+1);p[q]='Z';vals.append(sim.peek_observable_expectation(p))
 bad=ft.faults(d,cells,rule='clean')
 return dict(stim_target_pass=all(x==1 for x in vals),expectations=vals,clean_pass=not bad,clean_faults=len(bad),cx=sum(map(len,d['ops'])),depth=len(d['ops']))

class Model:
 def __init__(self,D,cap,seed=0,helpers=(),helper_x=False,backend='cadical195',max_measurements=12):
  self.D,self.cap,self.seed=D,cap,seed;self.cells=list(dict.fromkeys(B+C+list(helpers)));self.helper_x=helper_x
  self.rng=random.Random(seed);self.edges=[(u,v) for u in self.cells for v in nb(u) if v in self.cells];self.rng.shuffle(self.edges)
  self.n=0;self.clauses=[];self.val={};self.backend=backend;self.s=None;self.added=set();self.bas=basis(seed)
  self.true=self.nv();self.add([self.true])
  self.sel=[{e:self.nv() for e in self.edges} for _ in range(D)]
  self.ms=[{q:self.nv()for q in self.cells}for _ in range(D)]
  self.card([v for ss in self.ms for v in ss.values()],max_measurements)
  for t,ss in enumerate(self.ms):
   for q,z in ss.items():
    if t==D-1:self.add([-z])
    for tt in (t,t+1):
     if tt>=D:continue
     for e,v in self.sel[tt].items():
      if q in e:self.add([-z,-v])
    if t+1<D:self.add([-z,-self.ms[t+1][q]])
  for ss in self.sel:
   for q in self.cells:
    for a,b in itertools.combinations([v for e,v in ss.items() if q in e],2): self.add([-a,-b])
  self.card([v for ss in self.sel for v in ss.values()],cap)
  self.x=[{q:[self.nv() for _ in range(6)] for q in self.cells} for _ in range(D+1)]
  self.h=[{q:[self.nv() for _ in range(8)] for q in self.cells} for _ in range(D+1)]
  tar=target(self.cells)
  for q in self.cells:
   if q in B+C or not helper_x:
    v=transform(tar[q],self.bas)
    for b,z in enumerate(self.x[D][q]):self.add([z if (v>>b)&1 else -z])
   v=ft.sig({q},B)|(ft.sig({q},C)<<4)
   for b,z in enumerate(self.h[D][q]):self.add([z if (v>>b)&1 else -z])
  for t in reversed(range(D)):
   ss=self.sel[t]
   for q in self.cells:
    # State rows: inverse CX u->v changes v ^= u.
    ins=[(u,v) for u,v in self.edges if v==q]
    # Fault columns: pullback changes signature(u) ^= signature(v).
    outs=[(u,v) for u,v in self.edges if u==q]
    for ar,es,other in ((self.x,ins,0),(self.h,outs,1)):
     for b,z in enumerate(ar[t][q]):
      a=ar[t+1][q][b]
      self.add([self.ms[t][q]]+[ss[e] for e in es]+[-z,a]);self.add([self.ms[t][q]]+[ss[e] for e in es]+[z,-a])
      # MX followed by reset erases the row and any incoming X fault.
      self.add([-self.ms[t][q],-a if ar is self.x else -z])
      for e in es:self.xor_eq(z,[a,ar[t+1][e[other]][b]],guard=[-ss[e]])
  nz=[]
  for q in self.cells:
   z=self.nv();nz.append(z)
   for y in self.x[0][q]:self.add([-y,z])
   self.add([-z]+self.x[0][q])
  self.nz=dict(zip(self.cells,nz));self.card(nz,6)
  self.s=Solver(name=backend,bootstrap_with=self.clauses,use_timer=True);self.clauses=[]
  self.s.configure({'seed':seed})
 def nv(self):self.n+=1;return self.n
 def add(self,cl):
  if self.s is None:self.clauses.append(cl)
  else:self.s.add_clause(cl)
 def card(self,xs,k):
  if k>=len(xs):return
  enc=CardEnc.atmost(xs,bound=k,top_id=self.n,encoding=EncType.cardnetwrk)
  self.n=enc.nv
  for c in enc.clauses:self.add(c)
 def xor_eq(self,z,vs,guard=()):
  # Here at most two inputs; Tseitin CNF of z = xor(vs).
  if len(vs)==1:
   a=vs[0];self.add(list(guard)+[-z,a]);self.add(list(guard)+[z,-a]);return
  a,b=vs
  for c in ([a,b,-z],[-a,-b,-z],[a,-b,z],[-a,b,z]):self.add(list(guard)+c)
 def xor(self,a,b):
  z=self.nv();self.xor_eq(z,[a,b]);return z
 def cut(self,source):
  if source in self.added:return
  t,qs=source;self.added.add(source)
  sig=list(self.h[t][qs[0]])
  guard=[]
  if len(qs)==2:
   sig=[self.xor(a,b) for a,b in zip(sig,self.h[t][qs[1]])];guard=[-self.sel[t-1][qs]]
  dif=[self.xor(sig[i],sig[i+4]) for i in range(4)]
  for z in sig[:4]:self.add(guard+dif+[-z])
 def warm(self,d):
  layers=(d['ops']+[[]]*self.D)[:self.D];vals={}
  for t,ss in enumerate(self.sel):
   act={tuple(e) for e in layers[t]}
   for e,z in ss.items():vals[z]=e in act
   for q,z in self.ms[t].items():vals[z]=False
  ar={q:transform(v,self.bas) for q,v in target(self.cells).items()}
  hs={q:ft.sig({q},B)|(ft.sig({q},C)<<4) for q in self.cells}
  for t in reversed(range(self.D+1)):
   for q in self.cells:
    for b,z in enumerate(self.x[t][q]):vals[z]=bool(ar[q]>>b&1)
    for b,z in enumerate(self.h[t][q]):vals[z]=bool(hs[q]>>b&1)
   if t:
    for u,v in layers[t-1]:ar[v]^=ar[u];hs[u]^=hs[v]
  for q,z in self.nz.items():vals[z]=bool(ar[q])
  self.s.set_phases([z if v else -z for z,v in vals.items()])
 def candidate(self):
  mv={v for v in self.s.get_model() if v>0}
  return dict(ops=[[list(e) for e,v in ss.items() if v in mv] for ss in self.sel],measures=[[q for q,v in ss.items()if v in mv]for ss in self.ms],pivots=[q for q,z in self.nz.items() if z in mv],cells=self.cells,helper_x=self.helper_x)

def run(a):
 start=time.monotonic();m=Model(a.depth,a.cap,a.seed,[int(q) for q in a.helpers.split(',') if q],a.helper_x,a.backend,a.max_measurements)
 hint=json.loads(Path(a.hint).read_text()) if a.hint else None
 if hint:
  m.warm(hint)
  clipped=dict(hint,ops=(hint['ops']+[[]]*a.depth)[:a.depth])
  for f in ft.faults(clipped,m.cells,'clean'):m.cut(f[0])
 if a.eager:
  for t in range(a.depth+1):
   for q in m.cells:m.cut((t,(q,)))
 if a.fixed:
  for t,ss in enumerate(m.sel):
   act={tuple(e) for e in hint['ops'][t]}
   for e,z in ss.items():m.add([z if e in act else -z])
 elapsed=0.;it=0;sols=0;status='TIMEOUT';witness=None
 while elapsed<a.seconds:
  # Budget ends on solver return, retaining clauses across conflict-budget calls.
  m.s.conf_budget(20000)
  began=time.monotonic();ok=m.s.solve_limited();elapsed+=time.monotonic()-began;it+=1
  if ok is False:status='UNSAT';break
  if ok is None:continue
  sols+=1;d=m.candidate();v=verify(d)
  assert v['stim_target_pass'],v
  bad=ft.faults(d,m.cells,'clean')
  print(json.dumps(dict(event='candidate',iterations=it,models=sols,cx=v['cx'],bad=len(bad),solver_seconds=elapsed)),flush=True)
  if not bad:
   status='SAT';witness=dict(d,verification=v);break
  old=len(m.added)
  for f in bad:m.cut(f[0])
  assert len(m.added)>old
  m.warm(d)
 rec=dict(vars(a),status=status,solver_seconds=elapsed,wall_seconds=time.monotonic()-start,iterations=it,models=sols,cuts=len(m.added),variables=m.n,solver_stats=m.s.accum_stats(),basis=m.bas)
 if witness:
  rec['witness_cx']=sum(map(len,witness['ops']));rec['verification']=witness['verification']
  Path(a.out+'.prep.json').write_text(json.dumps(witness,indent=2)+'\n')
 Path(a.out+'.receipt.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec),flush=True)

def main():
 p=argparse.ArgumentParser();p.add_argument('--depth',type=int,required=True);p.add_argument('--cap',type=int,required=True);p.add_argument('--seed',type=int,default=0);p.add_argument('--seconds',type=float,default=7200);p.add_argument('--backend',default='cadical195');p.add_argument('--helpers',default='');p.add_argument('--helper-x',action='store_true');p.add_argument('--hint');p.add_argument('--eager',action='store_true');p.add_argument('--fixed',action='store_true');p.add_argument('--out',required=True);p.add_argument('--max-measurements',type=int,default=12)
 run(p.parse_args())
if __name__=='__main__':main()
