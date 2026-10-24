#!/home/jihoon/competitions/quantumn/.venv/bin/python
"""CP-SAT reverse endpoint benchmark on the v18 B+C footprint."""
import argparse,json,os,time
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
from ortools.sat.python import cp_model
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
def solve(depth,cap,cells,seconds,workers,seed):
 began=time.monotonic(); cells=list(cells); S=set(cells); edges=[(u,v) for u in cells for v in nb(u) if v in S]
 m=cp_model.CpModel(); sel=[]
 for t in range(depth):
  st={e:m.NewBoolVar(f's_{t}_{e[0]}_{e[1]}') for e in edges};sel.append(st)
  for q in cells:m.Add(sum(v for e,v in st.items() if q in e)<=1)
 x=[]
 for t in range(depth+1): x.append({(q,b):m.NewBoolVar(f'x_{t}_{q}_{b}') for q in cells for b in range(6)})
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
  z=m.NewBoolVar(f'nz_{q}');nz.append(z)
  bits=[x[0][q,b] for b in range(6)]
  for y in bits:m.AddImplication(y,z)
  m.AddBoolOr(bits+[z.Not()])
 m.Add(sum(nz)<=6);m.Add(sum(v for st in sel for v in st.values())<=cap)
 s=cp_model.CpSolver();s.parameters.max_time_in_seconds=seconds;s.parameters.num_search_workers=workers;s.parameters.random_seed=seed
 st=s.Solve(m);name=s.StatusName(st); status='SAT' if st in (cp_model.FEASIBLE,cp_model.OPTIMAL) else ('UNSAT' if st==cp_model.INFEASIBLE else 'TIMEOUT')
 out={'status':status,'depth':depth,'cap':cap,'cells':cells,'seconds':time.monotonic()-began,'workers':workers,'seed':seed}
 if status=='SAT':
  ops=[[list(e) for e,v in stx.items() if s.Value(v)] for stx in sel];out.update(cx=sum(map(len,ops)),ops=ops,input_support=[q for q,z in zip(cells,nz) if s.Value(z)])
 return out
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--depth',type=int,required=True);ap.add_argument('--cap',type=int,required=True);ap.add_argument('--seconds',type=float,default=300);ap.add_argument('--workers',type=int,default=8);ap.add_argument('--seed',type=int,default=0);ap.add_argument('--helpers',default='');ap.add_argument('--out',required=True);a=ap.parse_args()
 cells=list(dict.fromkeys(B+C+[int(x) for x in a.helpers.split(',') if x]));r=solve(a.depth,a.cap,cells,a.seconds,a.workers,a.seed);o=__import__('pathlib').Path(a.out);o.with_suffix('.endpoint.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
if __name__=='__main__':main()
