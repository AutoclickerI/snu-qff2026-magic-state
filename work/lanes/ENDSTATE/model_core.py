"""Read-only snapshot of ST1 placement/lifetime model; source is ST1/redesign.py.
Emitter intentionally not copied. Imported configuration is supplied by spacetime.py.
"""
import json,collections
from pathlib import Path
from ortools.sat.python import cp_model
def mappings(cells):
 rows=[]
 for sym in range(8):
  def tf(q):
   r,c=divmod(q,6);return [(r,c),(r,-c),(-r,c),(-r,-c),(c,r),(c,-r),(-c,r),(-c,-r)][sym]
  xy=[tf(q)for q in cells];mr=min(r for r,c in xy);mc=min(c for r,c in xy);hh=max(r for r,c in xy)-mr+1;ww=max(c for r,c in xy)-mc+1
  for dr in range(7-hh):
   for dc in range(7-ww):rows.append(dict(sym=sym,row=dr,col=dc,cells=[(r-mr+dr)*6+c-mc+dc for r,c in xy]))
 assert len(rows)==48
 return rows

def create(a):
 pre,dets=prefix();cells=sorted({q for u in pre for q in u.qs});embs=mappings(cells);horizon=a.max_round;m=cp_model.CpModel();R=m.NewIntVar(a.min_round,a.max_round,'R');xx=[];yy=[]
 def V(lo,hi,name):return m.NewIntVar(lo,hi,name)
 def occ(pos,start,end,name):
  s=V(0,horizon+3,name+'s');e=V(0,horizon+3,name+'e');z=V(0,horizon+3,name+'len');m.Add(s==start);m.Add(e==end);m.Add(z==e-s);xx.append(m.NewFixedSizeIntervalVar(pos,1,name+'cell'));yy.append(m.NewIntervalVar(s,z,e,name+'life'))
 embed=V(0,47,'embedding');mapping={q:V(0,35,f'prefix_cell{q}')for q in cells};m.AddAllowedAssignments([embed]+list(mapping.values()),[[i]+p['cells']for i,p in enumerate(embs)])
 if a.embedding>=0:m.Add(embed==a.embedding)
 elif not a.catalog:m.Add(embed<=5) # six classes modulo whole-grid D4
 pt=[V(0,horizon-1,f'prefix_t{i}')for i in range(len(pre))];per=collections.defaultdict(list)
 for i,u in enumerate(pre):
  m.Add(pt[i]<R)
  for q in u.qs:per[q].append(i)
 for q,seq in per.items():
  for i,j in zip(seq,seq[1:]):m.Add(pt[j]>pt[i])
  start=pt[seq[0]]
  for z,i in enumerate(seq):
   last=z+1==len(seq);resetnext=not last and pre[seq[z+1]].name in('RX','RESET')
   if last or resetnext:
    occ(mapping[q],start,pt[i]+1,f'prefix{q}_{i}')
    if not last:start=pt[seq[z+1]]
 T={};J=[];decisions=[];enc={k:encoder(a.encoder,k)for k in'abc'};cat=json.loads(Path(a.catalog).read_text())if a.catalog else None
 if cat and 'blocks'in cat:
  enc={k:([(cat['initial'][k].index(u),cat['initial'][k].index(v))for u,v in cat['blocks'][k]['ops']],[cat['initial'][k].index(q)for q in cat['blocks'][k]['pivots']])for k in'abc'}
 for k in'dabc':
  for i in range(7):
   key=f'{k}{i}';K=a.data_moves if k=='d'else a.moves;ps=[V(0,35,key+f'p{j}')for j in range(K+1)];init=V(0,horizon-1,key+'init');ts=[];moves=[]
   if k=='d':m.Add(ps[0]==mapping[PD[i]]);m.Add(init==pt[per[PD[i]][-1]]+1)
   for j in range(K):
    z=m.NewBoolVar(key+f'm{j}');t=V(1,horizon-1,key+f't{j}');m.AddAllowedAssignments([ps[j],ps[j+1],z],[(u,v,1)for u,v in ED]+[(q,q,0)for q in range(36)]);m.Add(t>=init+(k!='d'))
    if j:m.Add(z<=moves[-1]);m.Add(t>=ts[-1]+(2 if k=='d'else 1)*moves[-1])
    ts.append(t);moves.append(z)
   m.Add(ts[-1]+(2 if k=='d'else 1)*moves[-1]<=R)
   for j in range(K+1):occ(ps[j],init if j==0 else ts[j-1]-moves[j-1],R+(3 if k in'bd'else 2)if j==K else ts[j]+(3 if k=='d'else 2)*moves[j],key+f'_{j}')
   T[key]=dict(pos=ps,init=init,ts=ts,moves=moves);decisions+=ps+moves
 if a.compact9:
  assert a.encoder=='std9'and a.moves>=a.external_moves+2
  coords=[(0,1),(1,2),(0,2),(1,0),(0,0),(2,0),(1,1),(2,1),(2,2)];patterns=[]
  for sym in range(8):
   def tf(r,c):return [(r,c),(r,2-c),(2-r,c),(2-r,2-c),(c,r),(c,2-r),(2-c,r),(2-c,2-r)][sym]
   for dr in range(4):
    for dc in range(4):patterns.append([(rr+dr)*6+cc+dc for r,c in coords for rr,cc in[tf(r,c)]])
  for k in'abc':
   m.AddAllowedAssignments([T[f'{k}{i}']['pos'][0]for i in range(7)]+T[f'{k}5']['pos'][1:3],patterns)
   m.Add(T[f'{k}5']['moves'][0]==1);m.Add(T[f'{k}5']['moves'][1]==1)
   for i in range(7):
    cap=(2 if i==5 else 0)+a.external_moves
    if cap<a.moves:m.Add(T[f'{k}{i}']['moves'][cap]==0)
 for k in'dabc':
  jobs=[(i,)for i in range(7)]if k=='d'else enc[k][0];last={i:T[f'{k}{i}']['init']for i in range(7)}
  for gi,indices in enumerate(jobs):
   t=V(0,horizon-1,f'{k}g{gi}t');m.Add(t<R);loc=[];stages=[]
   for i in indices:
    tok=T[f'{k}{i}'];K=len(tok['moves']);stage=V(0,K,f'{k}g{gi}s{i}');p=V(0,35,f'{k}g{gi}p{i}');m.AddElement(stage,tok['pos'],p);m.Add(t>=last[i]+(k!='d'));last[i]=t;loc.append(p);stages.append(stage)
    if a.catalog:m.Add(stage==0)if k!='d'else None
    if a.compact9 and k!='d':m.Add(stage==(2 if i==5 and next(v for v in indices if v!=i)==1 else 0))
    for j in range(K+1):
     z=m.NewBoolVar(f'{k}g{gi}s{i}eq{j}');m.Add(stage==j).OnlyEnforceIf(z);m.Add(stage!=j).OnlyEnforceIf(z.Not())
     if j:m.Add(tok['moves'][j-1]==1).OnlyEnforceIf(z);m.Add(t>=tok['ts'][j-1]+(2 if k=='d'else 1)).OnlyEnforceIf(z)
     if j<K:m.Add(t<tok['ts'][j]).OnlyEnforceIf([z,tok['moves'][j]])
   if k!='d':m.AddAllowedAssignments(loc,ED)
   J.append(dict(k=k,indices=list(indices),t=t,loc=loc,stage=stages));decisions+=stages
 P={k:[V(0,6,f'{k}perm{i}')for i in range(7)]for k in'abc'};E={'d':[T[f'd{i}']['pos'][-1]for i in range(7)]}
 for k in'abc':
  m.AddAllowedAssignments(P[k],AUT);E[k]=[V(0,35,f'{k}end{i}')for i in range(7)]
  for i in range(7):m.AddElement(P[k][i],[T[f'{k}{j}']['pos'][-1]for j in range(7)],E[k][i])
 for i in range(7):
  for k,l in[('d','a'),('d','b'),('b','c')]:m.AddAllowedAssignments([E[k][i],E[l][i]],ED)
 m.AddAllDifferent(sum(E.values(),[]));m.AddNoOverlap2D(xx,yy)
 if a.catalog:
  assert 'blocks'in cat and all(len(cat['final'][k])==7 for k in'dabc'),'catalog needs explicit seven-wire encoders'
  for k in'abc':
   for i in range(7):
    m.Add(T[f'{k}{i}']['pos'][0]==cat['initial'][k][i]);m.Add(T[f'{k}{i}']['pos'][-1]==cat['final'][k][i]);m.Add(P[k][i]==P['a'][i])
  for i in range(7):m.AddElement(P['a'][i],cat['final']['d'],E['d'][i])
  # All 168 code automorphisms retain the catalog's physical encoded states.
  reachable=[]
  for ei,em in enumerate(embs):
   mp=dict(zip(cells,em['cells']))
   for pp in AUT:
    if all(abs(mp[PD[i]]//6-cat['final']['d'][pp[i]]//6)+abs(mp[PD[i]]%6-cat['final']['d'][pp[i]]%6)<=a.data_moves for i in range(7)):reachable.append([ei]+pp)
  m.AddAllowedAssignments([embed]+P['a'],reachable)
 # Search priority reflects the early-round target and measured exposure/move prices;
 # all resulting complete circuits are scored by full third order.
 cost=10000*R+sum(R-v['init']for v in T.values())+sum(R-j['t']for j in J)+sum(R-t for t in pt)+4*sum(z for v in T.values()for z in v['moves']);m.Minimize(cost)
 return m,dict(R=R,embedding=embed,mapping=mapping,prefix_t=pt,tokens=T,jobs=J,permutations=P,endpoints=E,space_intervals=xx,time_intervals=yy),pre,dets,embs,enc,decisions

def get(s,a,V,pre,dets,embs,enc):
 x=dict(args=vars(a),R=s.Value(V['R']),embedding=s.Value(V['embedding']),embedding_description=embs[s.Value(V['embedding'])],mapping={q:s.Value(v)for q,v in V['mapping'].items()},prefix_t=[s.Value(v)for v in V['prefix_t']],tokens={key:{k:[s.Value(v)for v in vs]if isinstance(vs,list)else s.Value(vs)for k,vs in tok.items()}for key,tok in V['tokens'].items()},jobs=[{k:[s.Value(v)for v in vs]if k in('loc','stage')else(s.Value(vs)if k=='t'else vs)for k,vs in j.items()}for j in V['jobs']],permutations={k:[s.Value(v)for v in vs]for k,vs in V['permutations'].items()},endpoints={k:[s.Value(v)for v in vs]for k,vs in V['endpoints'].items()},encoders=enc)
 return x
