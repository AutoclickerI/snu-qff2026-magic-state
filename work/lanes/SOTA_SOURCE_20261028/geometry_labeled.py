"""Joint labeled tile placement minimizes exact seven-coordinate transport distance."""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,time,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2];sys.path.insert(0,str(R/'work/lanes/SOTA_20261028'))
import tile_geometry as tg
from ortools.sat.python import cp_model
OLD=[6,20,19,10,2,22,16]
def sym(q,k):
 r,c=divmod(q,6)
 if k&4:c=5-c
 for _ in range(k&3):r,c=c,5-r
 return r*6+c

def solve(k,seconds=55):
 old=[sym(q,k)for q in OLD];m=cp_model.CpModel();T=tg.TILES;near=tg.NEAR;edges=tg.EDGES
 x=[[m.new_bool_var(f'x{i}_{j}')for j in range(len(T))]for i in range(7)]
 for i in range(7):m.add(sum(x[i])==1)
 occ={role:[m.new_bool_var(f'{role}{q}')for q in range(36)]for role in 'DABC'}
 for q in range(36):
  for j,role in enumerate('DABC'):
   m.add(occ[role][q]==sum(x[i][h]for i in range(7)for h,t in enumerate(T)if t[j]==q))
  m.add(sum(occ[role][q] for role in 'DABC')<=1)
 supports=[m.new_bool_var(f's{mask}')for mask in tg.MASKS];m.add(sum(supports)==1)
 square=[h for h,t in enumerate(T)if t[3] in near[t[1]]]
 for i in range(7):m.add(sum(x[i][h]for h in square)>=sum(supports[j]for j,mask in enumerate(tg.MASKS)if mask>>i&1))
 bc=[m.new_bool_var(f'bc{q}')for q in range(36)]
 for q in range(36):m.add(bc[q]==occ['B'][q]+occ['C'][q])
 def connect(used,n,tag,allowed):
  roots=[m.new_bool_var(f'r{tag}_{q}')for q in range(36)];m.add(sum(roots)==1)
  for q in range(36):
   m.add(roots[q]<=used[q])
   if q:m.add(sum(used[:q])==0).only_enforce_if(roots[q])
  flows={}
  for q,r in edges:
   z=m.new_int_var(0,n-1,f'f{tag}_{q}_{r}');m.add(z<=(n-1)*allowed[q]);m.add(z<=(n-1)*allowed[r]);flows[q,r]=z
  for q in range(36):m.add(sum(flows[q,r]for r in near[q])-sum(flows[r,q]for r in near[q])==n*roots[q]-used[q])
 connect(occ['A'],7,'A',occ['A']);connect(bc,14,'BC',[1-occ['A'][q]-occ['D'][q]for q in range(36)])
 cost=sum((abs(t[0]//6-old[i]//6)+abs(t[0]%6-old[i]%6))*x[i][j]for i in range(7)for j,t in enumerate(T))
 m.minimize(cost);solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=seconds;solver.parameters.num_search_workers=1;solver.parameters.random_seed=k+42
 status=solver.solve(m);res=dict(symmetry=k,status=solver.status_name(status),seconds=solver.wall_time,source_D=old,scope='Labeled tile geometry and exact Manhattan distance only; routing, resource preparation and full noisy circuit remain required.')
 if status in (cp_model.FEASIBLE,cp_model.OPTIMAL):
  tiles=[next(t for j,t in enumerate(T)if solver.value(x[i][j]))for i in range(7)]
  res.update(roles={r:[t[j] for t in tiles]for j,r in enumerate('DABC')},move_distance=round(solver.objective_value),lower_bound=solver.best_objective_bound,square_mask=sum(1<<i for i,t in enumerate(tiles)if t[3]in near[t[1]]),tiles=tiles)
 (H/f'geometry_labeled_sym{k}.json').write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res),flush=True);return res
if __name__=='__main__':
 with concurrent.futures.ProcessPoolExecutor(max_workers=2)as p:list(p.map(solve,[0,4]))
