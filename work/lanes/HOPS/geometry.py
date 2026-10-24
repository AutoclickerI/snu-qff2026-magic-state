from build import *
from ortools.sat.python import cp_model
from itertools import product
D0=[0,20,7,4,3,15,8]
def dist(a,b):return abs(a//6-b//6)+abs(a%6-b%6)
N={q:[r for r in range(36)if dist(q,r)==1]for q in range(36)}
auto=[]
for a,b,c in product(range(1,8),repeat=3):
 p=[((a if i&1 else 0)^(b if i&2 else 0)^(c if i&4 else 0))-1 for i in range(1,8)]
 if sorted(p)==list(range(7)):auto.append(p)

def solve(permute):
 m=cp_model.CpModel();ds=[];aa=[];bb=[];cc=[];costs=[]
 pa=[m.new_int_var(0,6,f'pa{i}')for i in range(7)];pb=[m.new_int_var(0,6,f'pb{i}')for i in range(7)]
 for p in [pa,pb]:
  if permute:m.add_allowed_assignments(p,auto)
  else:
   for i,x in enumerate(p):m.add(x==i)
 for i in range(7):
  d,a,b,c=[m.new_int_var(0,35,f'{k}{i}')for k in 'dabc'];dh=m.new_int_var(0,3,f'dh{i}');bh=m.new_int_var(0,6,f'bh{i}')
  tup=[]
  for d0 in range(36):
   dd=dist(D0[i],d0)
   if dd>3:continue
   for a0,b0 in product(N[d0],repeat=2):
    if a0==b0:continue
    for c0 in N[b0]:
     if c0 in(d0,a0):continue
     for ai in(range(7)if permute else[i]):
      ad=dist(A[ai],a0)
      if ad>2:continue
      for bi in(range(7)if permute else[i]):
       bd=dist(B[bi],b0);cd=dist(C[bi],c0)
       if bd<=2 and cd<=2:tup.append((d0,a0,b0,c0,ai,bi,dd,ad+bd+cd))
  m.add_allowed_assignments([d,a,b,c,pa[i],pb[i],dh,bh],tup);ds.append(d);aa.append(a);bb.append(b);cc.append(c);costs.append((dh,bh))
 m.add_all_different(ds+aa+bb+cc);DH=sum(x[0]for x in costs);BH=sum(x[1]for x in costs);m.add(DH<=5);m.minimize(3*DH+BH)
 s=cp_model.CpSolver();s.parameters.num_search_workers=1;s.parameters.max_time_in_seconds=90;s.parameters.cp_model_presolve=False
 status=s.solve(m);row=dict(permutations=permute,status=s.status_name(status),bound=s.best_objective_bound,stats=s.response_stats())
 if status in(cp_model.OPTIMAL,cp_model.FEASIBLE):row.update(d=[s.value(x)for x in ds],a=[s.value(x)for x in aa],b=[s.value(x)for x in bb],c=[s.value(x)for x in cc],pa=[s.value(x)for x in pa],pb=[s.value(x)for x in pb],data_hops=s.value(DH),block_distance=s.value(BH))
 (OUT/('geom_auto.json'if permute else'geom_fixed.json')).write_text(json.dumps(row,indent=2)+'\n');print(row,flush=True)
if __name__=='__main__':solve(False);solve(True)
