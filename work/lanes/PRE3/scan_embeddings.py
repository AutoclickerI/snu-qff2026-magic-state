import json,itertools,re
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn'); OUT=ROOT/'work/lanes/PRE3'
P0={0,1,2,3,4,6,7,8,9,10,13,14,15,19,20}; D0=[0,20,7,4,3,15,8]
def trans(tag,q):
 k,tr,tc=map(int,re.match(r's(\d+)_r(\d+)_c(\d+)',tag).groups()); r,c=divmod(q,6)
 z=[(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][k]
 allraw=[]
 for x in P0:
  a,b=divmod(x,6); allraw.append([(a,b),(a,5-b),(5-a,b),(5-a,5-b),(b,a),(b,5-a),(5-b,a),(5-b,5-a)][k])
 return (z[0]-min(a for a,b in allraw)+tr)*6+(z[1]-min(b for a,b in allraw)+tc)
def nb(q):
 r,c=divmod(q,6);return [x for x in (q-6 if r else -1,q+6 if r<5 else -1,q-1 if c else -1,q+1 if c<5 else -1) if x>=0]
rows=[]
for k in range(8):
 for tr in range(3):
  for tc in range(3):
   tag=f's{k}_r{tr}_c{tc}'; mp={q:trans(tag,q) for q in P0}
   if len(set(mp.values()))<len(P0) or any(not 0<=q<36 for q in mp.values()):continue
   d=[mp[q] for q in D0]; used=set(mp.values()); free=set(range(36))-used; per=[sorted(set(nb(x))&free) for x in d]; union=sorted(set().union(*map(set,per)))
   rows.append({'tag':tag,'data':d,'used':sorted(used),'free_partners':per,'distinct':len(union),'min_degree':min(map(len,per)),'sum_degree':sum(map(len,per))})
rows.sort(key=lambda x:(-x['distinct'],-x['min_degree'],-x['sum_degree'],x['tag']))
(OUT/'embedding_scan.json').write_text(json.dumps(rows,indent=2)+'\n')
for x in rows[:20]:print(x['tag'],'D',x['data'],'distinct',x['distinct'],'min',x['min_degree'],'sum',x['sum_degree'],'partners',x['free_partners'])
print('count',len(rows))
