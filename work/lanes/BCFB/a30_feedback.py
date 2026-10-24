"""Reverse-state SAT repair, with full v30f Fourier loss as the feedback objective."""
from a30_search import *
from synth import Model as Helpers,nb
from pysat.solvers import Solver

class Model(Helpers):
 def __init__(self,D,cap,seed):
  self.D=D;self.cells=A;self.n=0;self.clauses=[];self.s=None;self.rng=random.Random(seed)
  self.edges=[(u,v) for u in A for v in nb(u) if v in A];self.rng.shuffle(self.edges)
  self.sel=[{e:self.nv() for e in self.edges} for _ in range(D)]
  for ss in self.sel:
   for q in A:
    for x,y in itertools.combinations([v for e,v in ss.items() if q in e],2):self.add([-x,-y])
  self.card([v for ss in self.sel for v in ss.values()],cap)
  self.x=[{q:[self.nv() for _ in range(3)] for q in A} for _ in range(D+1)]
  self.h=[{q:[self.nv() for _ in range(4)] for q in A} for _ in range(D+1)]
  self.tar={q:i+1 for i,q in enumerate(A)}
  for q in A:
   for b,z in enumerate(self.x[D][q]):self.add([z if self.tar[q]>>b&1 else -z])
   for b,z in enumerate(self.h[D][q]):self.add([z if (self.tar[q]|8)>>b&1 else -z])
  for t in reversed(range(D)):
   for q in A:
    for ar,es,other in [(self.x,[e for e in self.edges if e[1]==q],0),(self.h,[e for e in self.edges if e[0]==q],1)]:
     for b,z in enumerate(ar[t][q]):
      a=ar[t+1][q][b];self.add([self.sel[t][e] for e in es]+[-z,a]);self.add([self.sel[t][e] for e in es]+[z,-a])
      for e in es:self.xor_eq(z,[a,ar[t+1][e[other]][b]],guard=[-self.sel[t][e]])
  self.nz={q:self.nv() for q in A}
  for q,z in self.nz.items():
   for y in self.x[0][q]:self.add([-y,z])
   self.add([-z]+self.x[0][q])
  self.card(list(self.nz.values()),3)
  # Exclude undetected logical X in the zero encoder, dual to logical Z on A.
  for t in range(D+1):
   for q in A:self.add(self.h[t][q][:3]+[-self.h[t][q][3]])
  for t in range(D):
   for e,z in self.sel[t].items():
    h=[self.xor(a,b) for a,b in zip(self.h[t+1][e[0]],self.h[t+1][e[1]])]
    self.add([-z]+h[:3]+[-h[3]])
  self.s=Solver(name='cadical195',bootstrap_with=self.clauses);self.s.configure({'seed':seed});self.clauses=[]
 def warm(self,layers):
  vals={};ar=dict(self.tar);hs={q:self.tar[q]|8 for q in A}
  for t,ss in enumerate(self.sel):
   act=set(map(tuple,layers[t]))
   for e,z in ss.items():vals[z]=e in act
  for t in reversed(range(self.D+1)):
   for q in A:
    for b,z in enumerate(self.x[t][q]):vals[z]=bool(ar[q]>>b&1)
    for b,z in enumerate(self.h[t][q]):vals[z]=bool(hs[q]>>b&1)
   if t:
    for u,v in layers[t-1]:ar[v]^=ar[u];hs[u]^=hs[v]
  for q,z in self.nz.items():vals[z]=bool(ar[q])
  self.s.set_phases([z if v else -z for z,v in vals.items()])
 def candidate(self):
  mv=set(v for v in self.s.get_model() if v>0)
  layers=[[e for e,z in ss.items() if z in mv] for ss in self.sel]
  e=dict(name='sat',pivots=[q for q in A if self.nz[q] not in mv],ops=[[v,u] for L in layers for u,v in L])
  self.add([-z if z in mv else z for ss in self.sel for z in ss.values()])
  return layers,e

def main(a):
 rng=random.Random(a.seed);m=Model(a.depth,a.cap,a.seed)
 _,_,_,us,ts,_,_,owned,_=source();layers=[]
 for t in sorted(set(ts[i] for i in owned if us[i].name=='CX')):layers.append([tuple(reversed(edge(us[i]))) for i in sorted(owned) if ts[i]==t and us[i].name=='CX'])
 while len(layers)<a.depth:layers.insert(rng.randrange(len(layers)+1),[])
 current=best=5.8239331514201564e-5;bestlayers=layers;m.warm(layers)
 db=sqlite3.connect(D/f'feedback_{a.seed}.sqlite');db.execute('create table if not exists results(id integer primary key,row text,witness blob,qasm blob,md text)')
 start=time.monotonic();n=0;it=0;seen=set()
 while time.monotonic()-start<a.seconds:
  it+=1;width=rng.choice([2,3,4,a.depth]);free=set(rng.sample(range(a.depth),min(width,a.depth)))
  ass=[]
  for t,ss in enumerate(m.sel):
   if t not in free:
    active=set(map(tuple,layers[t]));ass.extend(z if e in active else -z for e,z in ss.items())
  m.s.conf_budget(10000);ok=m.s.solve_limited(assumptions=ass)
  if ok is not True:continue
  ls,e=m.candidate();key=repr((e['pivots'],[(q,[x for x in e['ops'] if q in x]) for q in A]))
  if key in seen:continue
  seen.add(key)
  # Re-price several check choices in situ; lowest eligible score feeds back.
  trials=[]
  for checks in [[],[1,2,9],e['pivots']]:
   for R in [48,49,50]:
    t=dict(kind='prep',enc=e,checks=checks,R=R);r,text,md,_=work(t)
    if r['status']=='INVALID':continue
    n+=1;db.execute('insert into results values(?,?,?,?,?)',(n,json.dumps(r),zlib.compress(json.dumps(t).encode()),zlib.compress(text.encode()) if text else None,json.dumps(md)))
    if r.get('exp_minus_A1',0)>=.5002 and r.get('total',1)<1:trials.append((r['total'],r,text,md,t))
    break # earliest feasible R; separate timing search prices later schedules
  if not trials:continue
  val,r,text,md,t=min(trials,key=lambda x:x[0])
  if val<best:
   best=val;bestlayers=ls;stem=D/'finalists'/f'a30_fb_s{a.seed}_{n:05}'
   stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2));stem.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));print('BEST',stem.name,json.dumps(r),flush=True)
  temp=2e-7 if a.seed%2 else 0
  if val<current or (temp and rng.random()<math.exp(min(0,(current-val)/temp))):layers=ls;current=val
  if n%30==0:layers=bestlayers;current=best
  m.warm(layers);db.commit()
 rec=dict(vars(a),status='BUDGET_FINISHED',priced=n,unique=len(seen),iterations=it,best=best,seconds=time.monotonic()-start)
 db.commit();(D/'runs'/f'feedback_{a.seed}.receipt.json').write_text(json.dumps(rec,indent=2));print(json.dumps(rec),flush=True)
if __name__=='__main__':
 import math
 p=argparse.ArgumentParser();p.add_argument('--seed',type=int,required=True);p.add_argument('--depth',type=int,default=8);p.add_argument('--cap',type=int,default=16);p.add_argument('--seconds',type=int,default=1200);main(p.parse_args())
