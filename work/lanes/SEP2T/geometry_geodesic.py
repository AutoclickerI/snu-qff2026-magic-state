import os,sys,json,glob
from pathlib import Path
from collections import deque
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def distance(src,dst,blocked):
 seen={src};q=deque([(src,0)])
 while q:
  u,d=q.popleft()
  if u==dst:return d
  r,c=divmod(u,6)
  for v in (u-6 if r else -1,u+6 if r<5 else -1,u-1 if c else -1,u+1 if c<5 else -1):
   if v>=0 and v not in blocked and v not in seen:seen.add(v);q.append((v,d+1))
 return None
rows=[]
for p in sorted(HERE.glob('free_l3_auto_[0-9]*.json')):
 x=json.loads(p.read_text());blocked=set(x['final']['d']);ds=[distance(u,v,blocked) for k in 'bc' for u,v in zip(x['initial'][k],x['final'][k])]
 rows.append(dict(file=p.name,static_cost=x['cost'],data_distance=x['data_distance'],block_manhattan=x['block_distance'],block_geodesic=sum(ds) if None not in ds else None,max_geodesic=max(ds) if None not in ds else None))
(HERE/'geometry_geodesic.json').write_text(json.dumps(rows,indent=1));print(json.dumps(rows,indent=1))
