import os,sys,itertools,json,argparse
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
from ortools.sat.python import cp_model
HERE=os.path.dirname(__file__)
PRE=[0,20,7,4,3,15,8]
P=set([0,1,2,3,4,6,7,8,9,10,13,14,15,19,20]); F=set(range(36))-P

def nb(q):
 r,c=divmod(q,6);return [v for v in (q-6 if r else -1,q+6 if r<5 else -1,q-1 if c else -1,q+1 if c<5 else -1) if v>=0]
EDGES=[(u,v) for u in range(36) for v in nb(u)]
def paths(q,maxhop):
 out=[[q]]
 def rec(p):
  if len(p)-1>=maxhop:return
  for v in nb(p[-1]):
   if v in p:continue
   # shortest monotone only; final position can be any P cell
   pp=p+[v];out.append(pp);rec(pp)
 rec([q]);return [p for p in out if set(p)<=P]
LINES=[list(s) for s in itertools.combinations(range(7),3) if (s[0]+1)^(s[1]+1)^(s[2]+1)==0]

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=300);ap.add_argument('--workers',type=int,default=12);ap.add_argument('--count',type=int,default=20);ap.add_argument('--tag',default='g');ap.add_argument('--hops',type=int,default=6);ap.add_argument('--template',action='store_true');ap.add_argument('--parity',action='store_true');a=ap.parse_args()
 m=cp_model.CpModel()
 # role positions: d in pre cells, A/BC in released cells
 dom={'d':sorted(P),'a':sorted(F),'b':sorted(F),'c':sorted(F)}
 x={(k,i,q):m.NewBoolVar(f'{k}{i}_{q}') for k in 'dabc' for i in range(7) for q in dom[k]}
 pos={};col={}
 for k in 'dabc':
  for i in range(7):
   m.AddExactlyOne(x[k,i,q] for q in dom[k]);pos[k,i]=m.NewIntVar(0,35,f'{k}{i}');m.Add(pos[k,i]==sum(q*x[k,i,q] for q in dom[k]));col[k,i]=m.NewBoolVar(f'col{k}{i}');m.Add(col[k,i]==sum(((q//6+q%6)&1)*x[k,i,q] for q in dom[k]))
 for q in range(36):
  m.AddAtMostOne(x[k,i,q] for k in 'dabc' for i in range(7) if q in dom[k])
 for i in range(7):
  for k,l in [('d','a'),('d','b'),('b','c')]:
   m.AddAllowedAssignments([pos[k,i],pos[l,i]],EDGES);m.Add(col[k,i]+col[l,i]==1)
 # connectivity via flow for A and BC
 hb=[]
 for roles,n,root in [('a',7,'a'),('bc',14,'b')]:
  mem=[];absorb=[]
  for q in range(36):
   ab=sum(x[k,i,q] for k in roles for i in range(7) if q in dom[k]);mem.append(ab);absorb.append(ab)
  flow={e:m.NewIntVar(0,n,f'f{roles}{e[0]}_{e[1]}') for e in EDGES}
  for (u,v),z in flow.items():m.Add(z<=n*mem[u]);m.Add(z<=n*mem[v])
  for q in range(36):m.Add(sum(flow[q,v]-flow[v,q] for v in nb(q))==n*(x[root,0,q] if q in dom[root] else 0)-absorb[q])
 # template BC graph embedding / automorphism condition
 perm=[];permc=[]
 if a.template:
  autos=[]
  for v0,v1,v2 in itertools.permutations(range(1,8),3):
   images=[(v0 if n&1 else 0)^(v1 if n&2 else 0)^(v2 if n&4 else 0) for n in range(1,8)]
   if len(set(images))==7 and 0 not in images: autos.append([n-1 for n in images])
  perm=[m.NewIntVar(0,6,f'pb{i}') for i in range(7)];permc=[m.NewIntVar(0,6,f'pc{i}') for i in range(7)];m.AddAllowedAssignments(perm,autos);m.AddAllowedAssignments(permc,autos);m.Add(perm[1]!=permc[0])
  original={'b':[6,26,13,11,4,23,27],'c':[12,25,19,17,5,29,28]};mp={}
  for k in 'bc':
   for i,q in enumerate(original[k]):
    mp[q]=m.NewIntVar(0,35,f'mp{q}');m.AddElement(perm[i] if k=='b' else permc[i],[pos[k,j] for j in range(7)],mp[q])
  chain=[6,12,13,19,25,26,27,28,29,23,17,11,5,4]
  for u,v in zip(chain,chain[1:]):m.AddAllowedAssignments([mp[u],mp[v]],EDGES)
 if a.parity:
   # cats in P, not data/roles, three controls from an A line. pairwise at least 2 connected
   ids=[m.NewIntVar(0,6,f'id{j}') for j in range(3)];m.AddAllowedAssignments(ids,LINES)
   cats=[m.NewIntVar(0,35,f'cat{j}') for j in range(3)];m.AddAllDifferent(cats)
   targets=[]
   for j in range(3):
    t=m.NewIntVar(0,35,f't{j}');m.AddElement(ids[j],[pos['a',i] for i in range(7)],t);targets.append(t);m.AddAllowedAssignments([cats[j],t],EDGES)
    for i in range(7):m.Add(cats[j]!=pos['d',i])
    # cats in P and no role automatically due domains
   for u,v in itertools.combinations(targets,2):
    z=m.NewBoolVar('catadj');m.AddAllowedAssignments([cats[0] if False else u,v],EDGES).OnlyEnforceIf(z)
   # use table bool equivalence via forbidden is easier: require >=2 adjacent pair booleans
   zs=[]
   for i,j in itertools.combinations(range(3),2):
    z=m.NewBoolVar(f'cad{i}{j}');m.AddAllowedAssignments([cats[i],cats[j]],EDGES).OnlyEnforceIf(z);zs.append(z)
   m.Add(sum(zs)>=2)
 # data routes and endpoint P. Include no route collisions with final data positions.
 pv=[];chosen=[]
 for i,q0 in enumerate(PRE):
  ps=paths(q0,a.hops);vv=[m.NewBoolVar(f'p{i}_{j}') for j in range(len(ps))];pv.append(vv);m.AddExactlyOne(vv);m.Add(pos['d',i]==sum(p[-1]*v for p,v in zip(ps,vv)))
  # paths cannot pass through another final data role; and route ordering to avoid reused cells
  for j in range(7):
   if j==i:continue
   for p,v in zip(ps,vv):
    for q in p:m.Add(pos['d',j]!=q).OnlyEnforceIf(v)
  chosen.append(ps)
 # objective: round lower bound max(33, A depth 8, BC depth14, move 3*hops), plus hops and cat/data shape
 hops=[sum((len(p)-1)*v for p,v in zip(ps,vv)) for ps,vv in zip(chosen,pv)]
 rh=m.NewIntVar(33,80,'R_lb');m.Add(rh>=33+sum([]));m.Add(rh>=33+2*max(0,0))
 for h in hops:m.Add(rh>=33+3*h) # rough serialized move bound
 # punish data hops, max endpoint etc; enumerate solutions by exclusion
 m.Minimize(10000*rh+100*sum(hops)+sum(1 for _ in []))
 s=cp_model.CpSolver();s.parameters.max_time_in_seconds=a.seconds;s.parameters.num_workers=a.workers;s.parameters.random_seed=0
 count=0
 while count<a.count:
  st=s.Solve(m);print('STATUS',s.StatusName(st),'wall',s.WallTime(),flush=True)
  if st not in (cp_model.OPTIMAL,cp_model.FEASIBLE):break
  d={k:[s.Value(pos[k,i]) for i in range(7)] for k in 'dabc'}
  d.update(hBC=[],hA=[],M=[s.Value(z) for z in ids],cat=[s.Value(z) for z in cats],moves=[[q for q in ps] for ps,vv in zip(chosen,pv) for ps2,v in zip(ps,vv) if s.Value(v) for q in [ps2] if False],R_lb=s.Value(rh),hops=sum(s.Value(h) for h in hops))
  d['moves']=[next(ps for ps,v in zip(pss,vv) if s.Value(v)) for pss,vv in zip(chosen,pv)]
  if perm:d['template_perm']=[s.Value(z) for z in perm];d['template_permc']=[s.Value(z) for z in permc]
  out=os.path.join(HERE,f'{a.tag}_{count}.json');open(out,'w').write(json.dumps(d,indent=2)+'\n');print(out,json.dumps(d),flush=True);count+=1
  # exclude exact role positions and data endpoints to diversify
  lits=[]
  for k in 'dabc':
   for i in range(7):lits.append(x[k,i,d[k][i]])
  m.Add(sum(lits)<=len(lits)-1)
if __name__=='__main__':main()
