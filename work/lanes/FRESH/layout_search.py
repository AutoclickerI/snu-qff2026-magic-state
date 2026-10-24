from ortools.sat.python import cp_model
D=[0,20,7,4,3,15,8];A=[1,14,8,9,2,16,15]
nb=lambda q:[v for v in range(36) if abs(q//6-v//6)+abs(q%6-v%6)==1]
allowed=[q for q in range(36) if q not in set(D+A)]
m=cp_model.CpModel();B=[];C=[]
for i,d in enumerate(D):
 b=m.NewIntVarFromDomain(cp_model.Domain.FromValues([q for q in allowed if d in nb(q)]),f'b{i}');c=m.NewIntVarFromDomain(cp_model.Domain.FromValues(allowed),f'c{i}');B.append(b);C.append(c)
m.AddAllDifferent(B+C)
for i in range(7):m.AddAllowedAssignments([B[i],C[i]],[(b,c) for b in allowed for c in allowed if b!=c and c in nb(b)])
# encourage connected-ish: all cells span? no
ds=[]
for i in range(7):
 z=m.NewIntVar(0,36,f'd{i}');m.AddAbsEquality(z,B[i]-C[i]);ds.append(z)
m.Minimize(sum(ds))
s=cp_model.CpSolver();s.parameters.max_time_in_seconds=20;s.parameters.num_search_workers=4
for k in range(20):
 st=s.Solve(m)
 if st not in (cp_model.FEASIBLE,cp_model.OPTIMAL):print('stop',s.StatusName(st));break
 b=[s.Value(x) for x in B];c=[s.Value(x) for x in C];print(b,c)
 m.AddForbiddenAssignments(B+C,[b+c])
