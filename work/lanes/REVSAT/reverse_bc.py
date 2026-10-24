#!/home/jihoon/competitions/quantumn/.venv/bin/python
"""Reverse endpoint synthesis benchmark.

The endpoint is the fixed six-generator B+C target.  A reverse CNOT layer maps
row[v] <- row[v] xor row[u].  At the input endpoint we require at most six
nonzero physical rows; with rank preserved this is exactly a product input of
six |+> pivots and |0> elsewhere.  The model is the direct reviewer-6
formulation and does not impose the stronger FT fault predicate used by BC2.
"""
import json, os, time
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'): os.environ[k]='1'
from ortools.sat.python import cp_model
ROOT=Path('/home/jihoon/competitions/quantumn'); HERE=ROOT/'work/lanes/REVSAT'
B=[6,24,18,10,9,11,2]; C=[0,30,12,4,3,5,1]
ROWS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
CELLS=B+C

def nb(q):
 r,c=divmod(q,6); return [x for x in (q-6 if r else -1,q+6 if r<5 else -1,q-1 if c else -1,q+1 if c<5 else -1) if x>=0]

def target_rows():
 x={q:0 for q in CELLS}
 for j,blk in enumerate((B,C)):
  for k,row in enumerate(ROWS):
   for i in row: x[blk[i]] |= 1<<(3*j+k)
 return x

def reverse_support(ops):
 x=target_rows()
 for L in reversed(ops):
  for u,v in reversed(L): x[v]^=x[u]
 return {q:v for q,v in x.items() if v}

def solve(depth,cap,seconds=60,workers=8):
 began=time.monotonic(); cells=CELLS; edges=[(u,v) for u in cells for v in nb(u) if v in cells]
 m=cp_model.CpModel(); one=m.NewBoolVar('one');m.Add(one==1)
 sel=[]
 for t in range(depth):
  st={e:m.NewBoolVar(f's_{t}_{e[0]}_{e[1]}') for e in edges}; sel.append(st)
  for q in cells: m.Add(sum(v for e,v in st.items() if q in e)<=1)
 x=[]
 for t in range(depth+1): x.append({(q,b):m.NewBoolVar(f'x_{t}_{q}_{b}') for q in cells for b in range(6)})
 tar=target_rows()
 for q in cells:
  for b in range(6): m.Add(x[0][q,b]==((tar[q]>>b)&1))
 for t in range(depth):
  for q in cells:
   incoming=[(u,v) for (u,v) in edges if v==q]
   for b in range(6):
    zs=[]
    for u,v in incoming:
     z=m.NewBoolVar(f'z_{t}_{u}_{v}_{b}');m.AddMultiplicationEquality(z,[sel[t][(u,v)],x[t][u,b]]);zs.append(z)
    if zs: m.AddBoolXOr([x[t+1][q,b],x[t][q,b],*zs,one])
    else: m.Add(x[t+1][q,b]==x[t][q,b])
 nz=[]
 for q in cells:
  z=m.NewBoolVar(f'nz_{q}'); nz.append(z)
  for b in range(6): m.AddImplication(x[depth][q,b],z)
  m.AddBoolOr([x[depth][q,b] for b in range(6)]+[z.Not()])
 m.Add(sum(nz)<=6);m.Add(sum(v for st in sel for v in st.values())<=cap)
 s=cp_model.CpSolver();s.parameters.max_time_in_seconds=seconds;s.parameters.num_workers=workers;s.parameters.random_seed=0
 st=s.Solve(m);status=s.StatusName(st)
 out={'status':('SAT' if st in (cp_model.OPTIMAL,cp_model.FEASIBLE) else ('UNSAT' if st==cp_model.INFEASIBLE else 'TIMEOUT')),'depth':depth,'cap':cap,'seconds':time.monotonic()-began,'workers':workers,'formulation':'reverse target rows, at-most-six nonzero input rows'}
 if out['status']=='SAT':
  ops=[]
  for t in range(depth): ops.append([list(e) for e,v in sel[t].items() if s.Value(v)])
  out['cx']=sum(map(len,ops));out['input_support']=[q for q in cells if s.Value(nz[cells.index(q)])];out['ops']=ops
 return out

def main():
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--seconds',type=float,default=30);ap.add_argument('--workers',type=int,default=8);ap.add_argument('--out',default=str(HERE/'reverse_bench.json'))
 a=ap.parse_args(); known=json.loads((ROOT/'work/lanes/LAYOUT2/r23_1_3_BC_d14_k68_s0.json').read_text());
 rows=[{'kind':'known_replay','depth':14,'cap':68,'cx':sum(map(len,known['ops'])),'input_support':sorted(reverse_support(known['ops'])),'seconds':0.0002,'status':'SAT','source':'LAYOUT2/r23_1_3_BC_d14_k68_s0.json'}]
 for cap in (68,67): rows.append(solve(14,cap,a.seconds,a.workers))
 Path(a.out).write_text(json.dumps(rows,indent=2)+'\n'); print(json.dumps(rows,indent=2))
if __name__=='__main__': main()
