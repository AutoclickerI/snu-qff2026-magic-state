import os,sys,json,itertools
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from route import transform,nb
out=[]
for tr in range(3):
 for tc in range(2):
  P,D=transform(0,tr,tc);F=set(range(36))-P
  regs={frozenset([q]) for q in F}
  for size in range(1,7):regs={r|{v} for r in regs for q in r for v in nb(q) if v in F and v not in r}
  def conn(s):
   seen={min(s)}
   for _ in s:seen|={v for q in seen for v in nb(q) if v in s}
   return seen==s
  def matching(s):
   if not s:return []
   q=min(s,key=lambda q:sum(v in s for v in nb(q)))
   for v in nb(q):
    if v in s:
     z=matching(s-{q,v})
     if z is not None:return [(q,v)]+z
   return None
  good=[]
  for A in regs:
   BC=F-A
   if not conn(BC):continue
   mt=matching(BC)
   if mt is not None:good.append(dict(a=sorted(A),bc=sorted(BC),matching=mt))
  row=dict(transform=f'0,{tr},{tc}',connected_A_regions=len(regs),packings=len(good),examples=good[:3]);out.append(row);print(row,flush=True)
Path(__file__).with_name('packing.json').write_text(json.dumps(out,indent=2)+'\n')
