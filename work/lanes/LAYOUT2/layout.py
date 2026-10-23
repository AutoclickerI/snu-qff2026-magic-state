"""Grid layout + collision-free ordered data paths. R_lb is only a scheduling lower bound.
The encoder-dependent danger constraint is separated: exact enumeration screens
every geometric candidate, retaining only vectors caught by the selected M.
"""
import os, sys
sys.dont_write_bytecode = True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
import json, itertools, argparse
from pathlib import Path
from ortools.sat.python import cp_model
HERE=Path(__file__).resolve().parent
PRE=[0,20,7,4,3,15,8]
LINES=[list(s) for s in itertools.combinations(range(7),3) if (s[0]+1)^(s[1]+1)^(s[2]+1)==0]
def nb(q):
 r,c=divmod(q,6)
 return [rr*6+cc for rr,cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=rr<6 and 0<=cc<6]
EDGES=[(q,p) for q in range(36) for p in nb(q)]
def paths(q,maxhop):
 out=[[q]]
 def rec(p):
  if len(p)>maxhop: return
  for v in nb(p[-1]):
   if v in p: continue
   # shortest paths only; no arbitrary cyclic tours
   if abs(v//6-q//6)+abs(v%6-q%6)!=len(p): continue
   pp=p+[v];out.append(pp);rec(pp)
 rec([q]); return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seed',type=int,default=0);ap.add_argument('--seconds',type=float,default=180);ap.add_argument('--workers',type=int,default=8);ap.add_argument('--hops',type=int,default=3);ap.add_argument('--count',type=int,default=6);ap.add_argument('--tag',default='l');ap.add_argument('--maxhelpers',type=int,default=8);ap.add_argument('--maxtotal',type=int,default=99);ap.add_argument('--separated',action='store_true');ap.add_argument('--template',action='store_true');a=ap.parse_args()
 m=cp_model.CpModel();x={(k,i,q):m.NewBoolVar('') for k in 'dabc' for i in range(7) for q in range(36)}
 pos={}; col={}
 for k in 'dabc':
  for i in range(7):
   m.AddExactlyOne(x[k,i,q] for q in range(36));pos[k,i]=m.NewIntVar(0,35,'');m.Add(pos[k,i]==sum(q*x[k,i,q] for q in range(36)))
   col[k,i]=m.NewBoolVar('');m.Add(col[k,i]==sum(((q//6+q%6)%2)*x[k,i,q] for q in range(36)))
 for q in range(36): m.AddAtMostOne(x[k,i,q] for k in 'dabc' for i in range(7))
 for i in range(7):
  for k,l in [('d','a'),('d','b'),('b','c')]:
   m.AddAllowedAssignments([pos[k,i],pos[l,i]],EDGES);m.Add(col[k,i]+col[l,i]==1)
 perm=[];permc=[]
 if a.template:
  autos=[]
  for v0,v1,v2 in itertools.permutations(range(1,8),3):
   images=[(v0 if n&1 else 0)^(v1 if n&2 else 0)^(v2 if n&4 else 0) for n in range(1,8)]
   if len(set(images))==7 and 0 not in images:autos.append([n-1 for n in images])
  perm=[m.NewIntVar(0,6,'') for i in range(7)];m.AddAllowedAssignments(perm,autos)
  permc=[m.NewIntVar(0,6,'') for i in range(7)];m.AddAllowedAssignments(permc,autos)
  # Exact single-X propagation of the 73-CX template gives just one nontrivial
  # forbidden syndrome match: B syndrome 2 versus C syndrome 1.
  m.Add(perm[1]!=permc[0])
  original={'b':[6,26,13,11,4,23,27],'c':[12,25,19,17,5,29,28]};mp={}
  for k in 'bc':
   for i,q in enumerate(original[k]):
    mp[q]=m.NewIntVar(0,35,'');m.AddElement((perm if k=='b' else permc)[i],[pos[k,j] for j in range(7)],mp[q])
  chain=[6,12,13,19,25,26,27,28,29,23,17,11,5,4]
  for u,v in zip(chain,chain[1:]):m.AddAllowedAssignments([mp[u],mp[v]],EDGES)
  origin_color=m.NewBoolVar('')
  for k in 'bc':
   for i,q in enumerate(original[k]):
    cc=m.NewBoolVar('');m.AddElement((perm if k=='b' else permc)[i],[col[k,j] for j in range(7)],cc)
    m.Add(cc==origin_color if chain.index(q)%2==0 else cc+origin_color==1)
  if os.environ.get('FIX_TEMPLATE_B'):
   for i in range(7):m.Add(perm[i]==i)
 hb=[m.NewBoolVar('') for q in range(36)]
 m.Add(sum(hb)<=a.maxhelpers)
 for q in range(36): m.Add(sum(x[k,i,q] for k in 'dabc' for i in range(7))+hb[q]<=1)
 for roles,n,root in [('a',7,'a'),('bc',14,'b')]:
  mem=[];absorb=[]
  for q in range(36):
   ab=sum(x[k,i,q] for k in roles for i in range(7));absorb.append(ab)
   v=m.NewBoolVar('');m.Add(v==ab+(hb[q] if roles=='bc' else 0));mem.append(v)
  f={e:m.NewIntVar(0,n,'') for e in EDGES}
  for (u,v),z in f.items():m.Add(z<=n*mem[u]);m.Add(z<=n*mem[v])
  for q in range(36):m.Add(sum(f[q,p]-f[p,q] for p in nb(q))==n*x[root,0,q]-absorb[q])
 # A code labels hit by a cat; three simultaneous controls are mandatory.
 ids=[m.NewIntVar(0,6,'') for j in range(3)];m.AddAllowedAssignments(ids,LINES)
 cats=[m.NewIntVar(0,35,'') for j in range(3)];m.AddAllDifferent(cats)
 targets=[]
 for j in range(3):
  target=m.NewIntVar(0,35,'');m.AddElement(ids[j],[pos['a',i] for i in range(7)],target)
  targets.append(target)
  m.AddAllowedAssignments([cats[j],target],EDGES)
  for p in pos.values():m.Add(cats[j]!=p)
 if a.separated:
  for u,v in itertools.combinations(targets,2):m.AddForbiddenAssignments([u,v],EDGES)
 ce=[]
 for i,j in itertools.combinations(range(3),2):
  z=m.NewBoolVar('');m.AddAllowedAssignments([cats[i],cats[j]],EDGES).OnlyEnforceIf(z);ce.append(z)
 m.Add(sum(ce)>=2)
 pp=[paths(q,a.hops) for q in PRE]; pv=[]
 for i,ps in enumerate(pp):
  vv=[m.NewBoolVar('') for p in ps];pv.append(vv);m.AddExactlyOne(vv)
  m.Add(pos['d',i]==sum(p[-1]*v for p,v in zip(ps,vv)))
 order=[m.NewIntVar(0,6,'') for i in range(7)];m.AddAllDifferent(order)
 for i,(ps,vv) in enumerate(zip(pp,pv)):
  for p,v in zip(ps,vv):
   for j in range(7):
    if j==i:continue
    if PRE[j] in p[1:]:m.Add(order[i]>order[j]).OnlyEnforceIf(v)
    for q in p:
     m.Add(order[i]<order[j]).OnlyEnforceIf([v,x['d',j,q]])
 hops=[sum((len(p)-1)*v for p,v in zip(ps,vv)) for ps,vv in zip(pp,pv)]
 m.Add(sum(hops)<=a.maxtotal)
 rh=m.NewIntVar(33,60,'R_lb')
 for h in hops:m.Add(rh>=33+2*h)
 m.Minimize(1000*rh+10*sum(hops)+sum(hb))
 s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.random_seed=a.seed
 if os.environ.get('NO_PRESOLVE'):s.parameters.cp_model_presolve=False
 class Save(cp_model.CpSolverSolutionCallback):
  def __init__(self,ix):super().__init__();self.ix=ix;self.n=0
  def on_solution_callback(self):
   d={k:[self.Value(pos[k,i]) for i in range(7)] for k in 'dabc'}
   if perm:d['template_perm']=[self.Value(v) for v in perm];d['template_permc']=[self.Value(v) for v in permc]
   chosen={i:p for i,(ps,vv) in enumerate(zip(pp,pv)) for p,v in zip(ps,vv) if self.Value(v) and len(p)>1}
   d.update(hBC=[q for q in range(36) if self.Value(hb[q])],hA=[],M=[self.Value(i) for i in ids],cat=[self.Value(q) for q in cats],moves=[chosen[i] for i in sorted(chosen,key=lambda i:self.Value(order[i]))],R_lb=self.Value(rh),hops=sum(self.Value(h) for h in hops),objective=self.ObjectiveValue())
   self.last=d;self.n+=1
   path=HERE/f'{a.tag}_{self.ix}_{self.n}.json';path.write_text(json.dumps(d,indent=2)+'\n');print(path.name,json.dumps(d),flush=True)
 for ix in range(a.count):
  cb=Save(ix);st=s.Solve(m,cb);print('status',ix,s.StatusName(st),s.WallTime(),flush=True)
  if not cb.n:break
  d=cb.last
  # Diversify A's shape, rather than just swapping B and C labels.
  m.Add(sum(x['a',i,q] for i in range(7) for q in d['a'])<=6)
if __name__=='__main__':main()
