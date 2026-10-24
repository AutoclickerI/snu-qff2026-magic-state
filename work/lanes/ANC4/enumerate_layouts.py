import os,sys,json,itertools,collections
sys.dont_write_bytecode=True
from pathlib import Path
HERE=Path(__file__).resolve().parent
B0=[8,9,22,26,16,13,19];F0=[14,15,21,20];D0=[0,20,7,4,3,15,8]
def nb(q):return [x for x in range(36) if abs(q//6-x//6)+abs(q%6-x%6)==1]
NB={q:set(nb(q)) for q in range(36)}
def comps(qs):
 qs=set(qs);out=[]
 while qs:
  c={min(qs)};front=c.copy()
  while front:front=set().union(*(NB[x] for x in front))&qs-c;c|=front
  out.append(c);qs-=c
 return out

def assign(opts):
 order=sorted(range(7),key=lambda i:len(opts[i]));a=[None]*7
 def rec(k,used):
  if k==7:yield a.copy();return
  i=order[k]
  for q in opts[i]-used:a[i]=q;yield from rec(k+1,used|{q})
 yield from rec(0,set())

out=[];count=collections.Counter()
for sym in range(8):
 def tf(q):
  r,c=divmod(q,6);return [(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][sym]
 mr=min(tf(q)[0] for q in B0+F0);mc=min(tf(q)[1] for q in B0+F0)
 for dr in range(3):
  for dc in range(3):
   def mp(q):r,c=tf(q);return (r-mr+dr)*6+c-mc+dc
   B=list(map(mp,B0));F=list(map(mp,F0));busy=set(B+F)
   for D in assign([NB[b]-busy for b in B]):
    count['D_assignments']+=1
    for comp in comps(set(range(36))-busy-set(D)):
     opts=[NB[d]&comp for d in D]
     if any(not a for a in opts):continue
     for A in assign(opts):
      count['DA_assignments_connected_helpers']+=1
      dist=sum(abs(x//6-y//6)+abs(x%6-y%6) for x,y in zip(D0,D))
      ha=len(comp)-7
      out.append(dict(B=B,F=F,d=D,a=A,hA=sorted(comp-set(A)),distance=dist,helpers=ha,transform=[sym,dr,dc]))
# Keep closest layouts, dedup A mapping. Exact exhaustive fixed-checker-template extension domain.
out.sort(key=lambda x:(x['distance'],x['helpers']))
(HERE/'layout_enumeration.json').write_text(json.dumps(dict(counts=count,top=out[:100]),indent=2)+'\n')
print(dict(counts=count,total=len(out),top=out[:3]),flush=True)
