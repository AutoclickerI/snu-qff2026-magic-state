#!/home/jihoon/competitions/quantumn/.venv/bin/python
"""CP-SAT reverse endpoint synthesis with BC2 CEGAR fault constraints."""
import argparse,json,os,time
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
from ortools.sat.python import cp_model
import ft
B=[6,26,13,11,4,23,27]; C=[12,25,19,17,5,29,28]
ROWS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
def nb(q):
 r,c=divmod(q,6); return [x for x in (q-6 if r else -1,q+6 if r<5 else -1,q-1 if c else -1,q+1 if c<5 else -1) if x>=0]
def target(cells):
 x={q:0 for q in cells}
 for j,blk in enumerate((B,C)):
  for k,row in enumerate(ROWS):
   for i in row:x[blk[i]]|=1<<(3*j+k)
 return x
def build(depth,cap,cells,rule):
 cells=list(cells); S=set(cells); edges=[(u,v) for u in cells for v in nb(u) if v in S]; m=cp_model.CpModel(); sel=[]
 for t in range(depth):
  st={e:m.NewBoolVar(f's_{t}_{e[0]}_{e[1]}') for e in edges};sel.append(st)
  for q in cells:m.Add(sum(v for e,v in st.items() if q in e)<=1)
 x=[]
 for t in range(depth+1):x.append({(q,b):m.NewBoolVar(f'x_{t}_{q}_{b}') for q in cells for b in range(6)})
 tar=target(cells)
 for q in cells:
  for b in range(6):m.Add(x[depth][q,b]==((tar[q]>>b)&1))
 for t in range(depth-1,-1,-1):
  for q in cells:
   for b in range(6):
    zs=[]
    for u,v in edges:
     if v!=q:continue
     z=m.NewBoolVar(f'z_{t}_{u}_{v}_{b}');m.AddMultiplicationEquality(z,[sel[t][(u,v)],x[t+1][u,b]]);zs.append(z)
    if zs:m.AddBoolXOr([x[t][q,b].Not(),x[t+1][q,b],*zs])
    else:m.Add(x[t][q,b]==x[t+1][q,b])
 nz=[]
 for q in cells:
  z=m.NewBoolVar(f'nz_{q}');nz.append(z);bits=[x[0][q,b] for b in range(6)]
  for y in bits:m.AddImplication(y,z)
  m.AddBoolOr(bits+[z.Not()])
 m.Add(sum(nz)<=6);m.Add(sum(v for st in sel for v in st.values())<=cap)
 cache={}
 def andv(a,b):
  if isinstance(a,bool):return b if a else False
  if isinstance(b,bool):return a if b else False
  z=m.NewBoolVar('and');m.AddMultiplicationEquality(z,[a,b]);return z
 def xorv(vals):
  cs=sum(v is True for v in vals); vv=[v for v in vals if v is not None and v is not True and v is not False]
  if not vv:return bool(cs&1)
  # AddBoolXOr enforces odd parity.  Complement z for an even affine RHS.
  z=m.NewBoolVar('xor')
  lits=[z if (cs&1) else z.Not(), *vv]
  m.AddBoolXOr(lits)
  return z
 def propagate(src):
  if src in cache:return cache[src]
  t0,qs=src; f={v:(True if v in qs else None) for v in cells}
  for t in range(t0,depth):
   nf={}
   for v in cells:
    terms=[]
    for u in nb(v):
     if (u,v) in sel[t]:
      fu=f[u]
      if fu is None:continue
      terms.append(andv(sel[t][(u,v)],fu))
    cur=f[v]
    if cur is not None:terms.append(cur)
    nf[v]=xorv(terms) if terms else cur
   f=nf
  cache[src]=f;return f
 def parity(vals):return xorv(vals)
 def notlit(var):return (not var) if isinstance(var,bool) else var.Not()
 def lit_eq(var,bit):return var if bit else notlit(var)
 def add_fault(sources):
  fs=[propagate(z) for z in sources]; f={v:parity([g[v] for g in fs]) for v in cells};guard=[]
  for t,qs in sources:
   if len(qs)==2:guard.append(sel[t-1][qs].Not())
  sb=[parity([f[B[i]] for i in r]) for r in ROWS]+[parity([f[q] for q in B])]
  sc=[parity([f[C[i]] for i in r]) for r in ROWS]+[parity([f[q] for q in C])]
  ds=[parity([a,b]) for a,b in zip(sb,sc)]
  use='robust' if rule=='pairs' and len(sources)==1 else rule
  if rule=='allpairs':use='both' if len(sources)==1 else 'base'
  if use in ('clean','clean_literal','both'):
   vals=[f[q] for q in B] if use=='clean_literal' else sb
   for v in vals:m.AddBoolOr(guard+[d for d in ds]+[notlit(v)])
  if use not in ('clean','clean_literal'):
   diffs=[0]+sorted(ft.READ_FLIPS) if use in ('robust','both') else [0]
   for diff in diffs:
    for bval in range(16):
     if ft.dangerous(bval):
      m.AddBoolOr(guard+[lit_eq(d,(diff>>i)&1) for i,d in enumerate(ds)]+[lit_eq(v,0 if (bval>>i)&1 else 1) for i,v in enumerate(sb)])
 return m,sel,nz,cells,add_fault
def solve(depth,cap,cells,rule,seconds,workers,seed,hint=None):
 began=time.monotonic();m,sel,nz,cells,add_fault=build(depth,cap,cells,rule); added=set();it=0
 if hint:
  for t,layer in enumerate(hint.get('ops',[])):
   active={tuple(e) for e in layer}
   for e,var in sel[t].items():m.AddHint(var,1 if e in active else 0)
 while True:
  rem=seconds-(time.monotonic()-began)
  if rem<=0:return {'status':'TIMEOUT','seconds':time.monotonic()-began,'iters':it,'constraints':len(added)}
  s=cp_model.CpSolver();s.parameters.max_time_in_seconds=rem;s.parameters.num_search_workers=workers;s.parameters.random_seed=seed
  st=s.Solve(m);it+=1;name=s.StatusName(st);status='SAT' if st in (cp_model.FEASIBLE,cp_model.OPTIMAL) else ('UNSAT' if st==cp_model.INFEASIBLE else 'TIMEOUT')
  if status!='SAT':return {'status':status,'seconds':time.monotonic()-began,'iters':it,'constraints':len(added)}
  ops=[[list(e) for e,v in se.items() if s.Value(v)] for se in sel];d={'ops':ops,'pivots':[q for q,z in zip(cells,nz) if s.Value(z)]}
  bad=[] if rule=='none' else [f for f in ft.faults(d,cells,rule,limit=256) if f not in added]
  print(json.dumps({'iter':it,'bad':len(bad),'added':len(added),'seconds':time.monotonic()-began}),flush=True)
  if not bad:return {'status':'SAT','seconds':time.monotonic()-began,'iters':it,'constraints':len(added),'cx':sum(map(len,ops)),'ops':ops,'pivots':d['pivots']}
  for f in bad:add_fault(f);added.add(f)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--depth',type=int,required=True);ap.add_argument('--cap',type=int,required=True);ap.add_argument('--seconds',type=float,default=300);ap.add_argument('--workers',type=int,default=8);ap.add_argument('--seed',type=int,default=0);ap.add_argument('--helpers',default='');ap.add_argument('--rule',default='both');ap.add_argument('--hint');ap.add_argument('--out',required=True);a=ap.parse_args();cells=list(dict.fromkeys(B+C+[int(x) for x in a.helpers.split(',') if x]));hint=json.load(open(a.hint)) if a.hint else None;r=solve(a.depth,a.cap,cells,a.rule,a.seconds,a.workers,a.seed,hint);r.update(depth=a.depth,cap=a.cap,cells=cells,rule=a.rule,seed=a.seed);o=__import__('pathlib').Path(a.out);o.with_suffix('.receipt.json').write_text(json.dumps({k:v for k,v in r.items() if k not in ('ops',)},indent=2)+'\n');
 if 'ops' in r:o.with_suffix('.prep.json').write_text(json.dumps({'ops':r['ops'],'pivots':r['pivots'],'depth':a.depth,'cx':r['cx'],'cells':cells,'rule':a.rule},indent=2)+'\n')
 print(json.dumps({k:v for k,v in r.items() if k not in ('ops',)}),flush=True)
if __name__=='__main__':main()
