"""Unlabelled A-D-B-C paths with connected B/C, then minimum-distance labels."""
from common import *
import argparse
from scipy.optimize import linear_sum_assignment
EDGES=[(a,b)for a in range(36)for b in range(36)if abs(a//6-b//6)+abs(a%6-b%6)==1]
PD=[0,20,7,4,3,15,8];P={0,1,2,3,4,6,7,8,9,10,13,14,15,19,20}
def main():
 p=argparse.ArgumentParser();p.add_argument('--seconds',type=float,default=120);p.add_argument('--workers',type=int,default=2);p.add_argument('--a-connect',action='store_true');p.add_argument('--tag',default='unlabelled');p.add_argument('--count',type=int,default=8);a=p.parse_args()
 m=cp_model.CpModel();mem={(k,q):m.NewBoolVar(f'{k}{q}')for k in'abcd'for q in range(36)}
 for k in'abcd':m.Add(sum(mem[k,q]for q in range(36))==7)
 for q in range(36):m.Add(sum(mem[k,q]for k in'abcd')<=1)
 ee={}
 for k,l in [('a','d'),('d','b'),('b','c')]:
  es={e:m.NewBoolVar(f'{k}{l}{e}')for e in EDGES};ee[k,l]=es
  for q in range(36):
   m.Add(sum(z for (u,v),z in es.items()if u==q)==mem[k,q]);m.Add(sum(z for(u,v),z in es.items()if v==q)==mem[l,q])
 for k in ('abc'if a.a_connect else'bc'):
  roots=[m.NewBoolVar(f'root{k}{q}')for q in range(36)];m.AddExactlyOne(roots)
  for q,z in enumerate(roots):
   m.Add(z<=mem[k,q])
   for v in range(q):m.Add(z+mem[k,v]<=1)
  fs={e:m.NewIntVar(0,6,f'f{k}{e}')for e in EDGES}
  for(u,v),z in fs.items():m.Add(z<=6*mem[k,u]);m.Add(z<=6*mem[k,v])
  for q in range(36):m.Add(sum(z-fs[v,u]for(u,v),z in fs.items()if u==q)==7*roots[q]-mem[k,q])
 # Prefer usable exterior cells, without rejecting placements elsewhere.
 m.Minimize(sum(mem[k,q]for k in'bc'for q in P))
 s=cp_model.CpSolver();s.parameters.num_workers=a.workers;s.parameters.max_time_in_seconds=a.seconds;s.parameters.cp_model_presolve=False;s.parameters.stop_after_first_solution=True
 for it in range(a.count):
  st=s.Solve(m);r=dict(status=s.StatusName(st),seconds=s.WallTime(),args=vars(a),iteration=it)
  if st not in(cp_model.FEASIBLE,cp_model.OPTIMAL):
   append_result(a.tag,r,'Unlabelled static matching and connected regions; bounded solver result.');break
  matches={k:{u:v for(u,v),z in es.items()if s.Value(z)}for k,es in ee.items()};da={v:u for u,v in matches['a','d'].items()};ds=sorted(da)
  cost=[[abs(x//6-y//6)+abs(x%6-y%6)for y in ds]for x in PD];ii,jj=linear_sum_assignment(cost);lay={k:[]for k in'dabc'}
  for j in jj:
   d=ds[j];b=matches['d','b'][d];c=matches['b','c'][b]
   for k,q in [('a',da[d]),('d',d),('b',b),('c',c)]:lay[k].append(q)
  r.update(layout=lay,hops=sum(cost[i][j]for i,j in zip(ii,jj)));name=f'{a.tag}_{it}'
  (H/(name+'.json')).write_text(json.dumps(r,indent=2));append_result(name,r,'Unlabelled connected-block geometry; encoder and route remain to be built.');print(json.dumps(r),flush=True)
  m.Add(sum(mem[k,q]for k in'abcd'for q in lay[k])<=27)
if __name__=='__main__':main()
