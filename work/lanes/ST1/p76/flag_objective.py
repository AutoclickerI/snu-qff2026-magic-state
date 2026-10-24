"""Exact local single-fault phase classes as CP-SAT proposal cost.

Integer units: CX atom=1, one-qubit depolarizing atom=5, reset flip=15.
The objective is diagnostic, and never replaces full-circuit all-orders rank.
"""
def build(m,G,times,edges,A,piv,flag):
 n=len(times);badcodes=[i+1 for i in flag]
 def label(name,width):
  bits=[m.NewBoolVar(name+'b'+str(j))for j in range(width)];v=m.NewIntVar(0,(1<<width)-1,name);m.Add(v==sum((1<<j)*b for j,b in enumerate(bits)));return v,bits
 z=[[label(f'z{t}_{i}',4)for i in range(7)]for t in range(n+1)];x=[[label(f'x{t}_{i}',3)for i in range(7)]for t in range(n+1)]
 def equal(v,k,name):
  b=m.NewBoolVar(name);m.Add(v==k).OnlyEnforceIf(b);m.Add(v!=k).OnlyEnforceIf(b.Not());return b
 def bad(v,name):
  b=m.NewBoolVar(name);m.AddAllowedAssignments([v,b],[(j,int(j in badcodes))for j in range(16)]);return b
 def both(bs,name):
  b=m.NewBoolVar(name);m.AddBoolAnd(bs).OnlyEnforceIf(b);m.AddBoolOr([v.Not()for v in bs]).OnlyEnforceIf(b.Not());return b
 def xor(a,b,out,condition=None):
  for aa,bb,cc in zip(a,b,out):
   c=m.AddAllowedAssignments([aa,bb,cc],[(0,0,0),(0,1,1),(1,0,1),(1,1,0)])
   if condition is not None:c.OnlyEnforceIf(condition)
 for i in range(7):m.Add(z[n][i][0]==(i+1)|8);m.Add(x[n][i][0]==i+1)
 busy={};cost=[]
 for ti,t in enumerate(times):
  for i in range(7):
   inc=[G[t,u,v]for u,v in edges if i in(u,v)];busy[ti,i]=m.NewBoolVar(f'busy{ti}_{i}');m.Add(busy[ti,i]==sum(inc))
   zg=[G[t,u,v]for u,v in edges if v==i];xg=[G[t,u,v]for u,v in edges if u==i]
   m.Add(z[ti][i][0]==z[ti+1][i][0]).OnlyEnforceIf([g.Not()for g in zg]);m.Add(x[ti][i][0]==x[ti+1][i][0]).OnlyEnforceIf([g.Not()for g in xg])
   for u,v in edges:
    if v==i:xor(z[ti+1][v][1],z[ti+1][u][1],z[ti][v][1],G[t,u,v])
    if u==i:xor(x[ti+1][u][1],x[ti+1][v][1],x[ti][u][1],G[t,u,v])
  for u,v in edges:
   g=G[t,u,v];zz,bits=label(f'zz{ti}_{u}_{v}',4);xor(z[ti+1][u][1],z[ti+1][v][1],bits)
   bads=[bad(val,f'bad{ti}_{u}_{v}_{j}')for j,val in enumerate([z[ti+1][u][0],z[ti+1][v][0],zz])]
   xu,xv=x[ti+1][u][0],x[ti+1][v][0];eq=m.NewBoolVar(f'xeq{ti}_{u}_{v}');m.Add(xu==xv).OnlyEnforceIf(eq);m.Add(xu!=xv).OnlyEnforceIf(eq.Not())
   mult=m.NewIntVar(1,4,f'mult{ti}_{u}_{v}');m.Add(mult==1+equal(xu,0,f'xu0{ti}_{u}_{v}')+equal(xv,0,f'xv0{ti}_{u}_{v}')+eq)
   bsum=m.NewIntVar(0,3,f'bsum{ti}_{u}_{v}');m.Add(bsum==sum(bads));val=m.NewIntVar(0,12,f'cost{ti}_{u}_{v}');m.AddMultiplicationEquality(val,[g,bsum,mult]);cost.append(val)
 for i in range(7):
  had=m.NewConstant(0)
  for ti,t in enumerate(times):
   first=both([busy[ti,i],had.Not()],f'first{ti}_{i}');binit=bad(z[ti][i][0],f'bi{ti}_{i}');cost.append(15*both([first,piv[i],binit],f'pi{ti}_{i}'))
   bidle=bad(z[ti+1][i][0],f'bd{ti}_{i}');idle=both([had,busy[ti,i].Not(),bidle],f'id{ti}_{i}');cost.append(5*idle);cost.append(5*both([idle,equal(x[ti+1][i][0],0,f'ix0{ti}_{i}')],f'iy{ti}_{i}'))
   nxt=m.NewBoolVar(f'had{ti}_{i}');m.AddMaxEquality(nxt,[had,busy[ti,i]]);had=nxt
 return sum(cost)
