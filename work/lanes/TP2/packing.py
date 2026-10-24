import os,sys,json,itertools,time
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
D=[0,20,7,4,3,15,8]
P={0,1,2,3,4,6,7,8,9,10,13,14,15,19,20}
F=set(range(36))-P
HERE=Path(__file__).resolve().parent

def nb(q):
 r,c=divmod(q,6)
 return [rr*6+cc for rr,cc in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)) if 0<=rr<6 and 0<=cc<6]

def conn(s):
 if not s:return False
 seen={min(s)}
 while True:
  x=seen|{v for q in seen for v in nb(q) if v in s}
  if seen==x:return seen==set(s)
  seen=x

def match(b,c):
 if not b:return [[]]
 q=min(b,key=lambda q:sum(v in c for v in nb(q)))
 out=[]
 for v in nb(q):
  if v in c:
   out += [[(q,v)]+t for t in match(b-{q},c-{v})]
 return out

def run():
 regs={frozenset([q]) for q in F}
 for size in range(1,7):regs={r|{v} for r in regs for q in r for v in nb(q) if v in F and v not in r}
 packs=[]
 for O in sorted(regs,key=lambda r:tuple(sorted(r))):
  rest=F-O
  for B in regs:
   if not B<=rest:continue
   C=rest-B
   if not conn(C):continue
   mt=match(set(B),set(C))
   for pairs in mt:
    dist=sum(min(abs(d//6-o//6)+abs(d%6-o%6) for o in O)-1 for d in D)
    packs.append(dict(o=sorted(O),b=sorted(B),c=sorted(C),pairs=pairs,dist=dist))
 packs.sort(key=lambda p:p['dist'])
 (HERE/'packing.json').write_text(json.dumps(dict(regions=len(regs),packings=packs),indent=2))
 print('regions',len(regs),'packings',len(packs),'best',packs[:5],flush=True)
if __name__=='__main__':run()

def staged():
 regs={frozenset([q]) for q in F}
 for size in range(1,7):regs={r|{v} for r in regs for q in r for v in nb(q) if v in F and v not in r}
 pairs=[]
 for B in regs:
  for C in regs:
   if B&C:continue
   for mt in match(set(B),set(C)):
    for O in regs:
     if B&O:continue
     ds=sum(min(abs(d//6-o//6)+abs(d%6-o%6) for o in O)-1 for d in D)
     pairs.append(dict(o=sorted(O),b=sorted(B),c=sorted(C),pairs=mt,dist=ds))
 pairs.sort(key=lambda p:(p['dist'],sum(p['o'])))
 (HERE/'staged_packing.json').write_text(json.dumps(dict(regions=len(regs),packings=pairs),indent=2))
 print('staged',len(pairs),'best',pairs[:3],flush=True)

def helpers():
 regs={frozenset([q]) for q in F}
 for size in range(1,7):regs={r|{v} for r in regs for q in r for v in nb(q) if v in F and v not in r}
 out=[]
 for O in regs:
  for B in regs:
   if O&B or not conn(F-B):continue
   C=F-B-O
   for mt in match(set(B),set(C)):
    ds=sum(min(abs(d//6-o//6)+abs(d%6-o%6) for o in O)-1 for d in D)
    out.append(dict(o=sorted(O),b=sorted(B),c=sorted(C),pairs=mt,dist=ds))
 out.sort(key=lambda p:p['dist'])
 (HERE/'helper_packing.json').write_text(json.dumps(dict(packings=out),indent=2))
 print('helpers',len(out),'best',out[:3],flush=True)
