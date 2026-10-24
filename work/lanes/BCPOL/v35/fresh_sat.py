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
import ft
B,C,ROWS=ft.B,ft.C,ft.ROWS
HERE=Path(__file__).resolve().parent

def nb(q):
 r,c=divmod(q,6)
 return [u for u in (q-6 if r else -1,q+6 if r<5 else -1,q-1 if c else -1,q+1 if c<5 else -1) if u>=0]

def target(cells):
 return {q:sum(1<<k for k,row in enumerate(ROWS) if any(q in {blk[i] for i in row} for blk in (B,C))) for q in cells}

def endpoint_signature(q):
 return ft.sig({q},B) | sum(int(q in (b,c))<<(4+i) for i,(b,c) in enumerate(zip(B,C)))

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
 for l in d['ops']:
  used=set()
  for u,v in l:
   assert v in nb(u) and u not in used and v not in used
   used|={u,v};c.append('CX',[u,v])
 sim=stim.TableauSimulator();sim.do(c)
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
 def __init__(self,D,cap,seed=0,helpers=(),helper_x=False,backend='cadical195'):
  self.D,self.cap,self.seed=D,cap,seed;self.cells=list(dict.fromkeys(B+C+list(helpers)));self.helper_x=helper_x
  self.rng=random.Random(seed);self.edges=[(u,v) for u in self.cells for v in nb(u) if v in self.cells];self.rng.shuffle(self.edges)
  self.n=0;self.clauses=[];self.val={};self.backend=backend;self.s=None;self.added=set();self.bas=basis(seed)
  self.true=self.nv();self.add([self.true])
  self.sel=[{e:self.nv() for e in self.edges} for _ in range(D)]
  for ss in self.sel:
   for q in self.cells:
    for a,b in itertools.combinations([v for e,v in ss.items() if q in e],2): self.add([-a,-b])
  self.card([v for ss in self.sel for v in ss.values()],cap)
  self.x=[{q:[self.nv() for _ in range(3)] for q in self.cells} for _ in range(D+1)]
  self.h=[{q:[self.nv() for _ in range(11)] for q in self.cells} for _ in range(D+1)]
  tar=target(self.cells)
  for q in self.cells:
   if q in B+C or not helper_x:
    v=transform(tar[q],self.bas)
    for b,z in enumerate(self.x[D][q]):self.add([z if (v>>b)&1 else -z])
   v=endpoint_signature(q)
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
      self.add([ss[e] for e in es]+[-z,a]);self.add([ss[e] for e in es]+[z,-a])
      for e in es:self.xor_eq(z,[a,ar[t+1][e[other]][b]],guard=[-ss[e]])
  nz=[]
  for q in self.cells:
   z=self.nv();nz.append(z)
   for y in self.x[0][q]:self.add([-y,z])
   self.add([-z]+self.x[0][q])
  self.nz=dict(zip(self.cells,nz));self.card(nz,3)
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
  ar={q:transform(v,self.bas) for q,v in target(self.cells).items()}
  hs={q:endpoint_signature(q) for q in self.cells}
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
  return dict(ops=[[list(e) for e,v in ss.items() if v in mv] for ss in self.sel],pivots=[q for q,z in self.nz.items() if z in mv],cells=self.cells,helper_x=self.helper_x)
