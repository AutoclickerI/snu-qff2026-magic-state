import json,random
from pathlib import Path
OLD=[6,20,19,10,2,22,16];NEW=[10,20,19,16,2,22,28]
perms=[]
for a in range(1,8):
 for b in range(1,8):
  for c in range(1,8):
   p=[(a if i&1 else 0)^(b if i&2 else 0)^(c if i&4 else 0)for i in range(1,8)]
   if len(set(p))==7:perms.append([x-1 for x in p])
def sym(q,k):
 r,c=divmod(q,6)
 if k&4:c=5-c
 for _ in range(k&3):r,c=c,5-r
 return r*6+c
res=[]
for k in range(8):
 a=[sym(q,k)for q in OLD]
 for p in perms:
  d=sum(abs(q//6-NEW[p[i]]//6)+abs(q%6-NEW[p[i]]%6)for i,q in enumerate(a))
  res.append(dict(distance=d,symmetry=k,source_D=a,map_source_index_to_final_index=p,source_to_target=list(zip(a,[NEW[p[i]]for i in range(7)]))))
res.sort(key=lambda r:r['distance']);print(json.dumps(res[:30],indent=2));Path(__file__).with_suffix('.json').write_text(json.dumps(res,indent=2)+'\n')
