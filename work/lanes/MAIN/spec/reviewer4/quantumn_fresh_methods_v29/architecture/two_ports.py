"""Enumerate connected7-cell blocks in6x6 and require two private external ports.

Each block site needs two different neighbouring cells, and all14 selected
external neighbours must be distinct (e.g. one data and one routing helper).
This necessary condition precedes any A/C connectivity or encoder requirement.
"""
from pathlib import Path
import json

N=6;n=N*N
nb=[]
for q in range(n):
 r,c=divmod(q,N)
 nb.append([rr*N+cc for rr,cc in [(r-1,c),(r+1,c),(r,c-1),(r,c+1)] if 0<=rr<N and 0<=cc<N])
masks=[sum(1<<j for j in ns) for ns in nb]
sets={1<<q for q in range(n)}
counts={1:len(sets)}
for size in range(2,8):
 nxt=set()
 for S in sets:
  border=0;x=S
  while x:
   t=x&-x;x-=t;border|=masks[t.bit_length()-1]
  border &= ~S
  while border:
   t=border&-border;border-=t;nxt.add(S|t)
 sets=nxt;counts[size]=len(sets)

tested=0;feasible=[];maxmatch=0;degree_ok=0
for S in sets:
 qs=[q for q in range(n) if S>>q&1]
 ports={q:[j for j in nb[q] if not(S>>j&1)] for q in qs}
 if any(len(ports[q])<2 for q in qs):continue
 degree_ok+=1
 left=[(q,k) for q in qs for k in range(2)]
 owner={}
 def augment(v,seen):
  q,k=v
  for j in ports[q]:
   if j in seen:continue
   seen.add(j)
   if j not in owner or augment(owner[j],seen):owner[j]=v;return True
  return False
 matched=sum(augment(v,set()) for v in left)
 maxmatch=max(maxmatch,matched);tested+=1
 if matched==14:feasible.append(qs)
out=dict(grid=[N,N],connected_subsets_by_size=counts,degree_eligible_blocks=degree_ok,
 full_matching_tested=tested,largest_matching=maxmatch,feasible_count=len(feasible),feasible_blocks=feasible)
Path(__file__).with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
