import itertools,json
from pathlib import Path
D=[6,20,19,10,2,22,16];B=[12,26,25,11,3,28,17];fixed=set(D+B)
def nb(q):return [r for r in range(36) if abs(q//6-r//6)+abs(q%6-r%6)==1]
opts=[]
for d,b in zip(D,B):
 opts.append([(a,c,abs(a//6-c//6)+abs(a%6-c%6)==1) for a in nb(d) for c in nb(b) if a not in fixed and c not in fixed and a!=c])
results=[]
def walk(i,used,path):
 if i==7:
  results.append((sum(x[2] for x in path),path));return
 for a,c,s in opts[i]:
  if a not in used and c not in used:walk(i+1,used|{a,c},path+[(a,c,s)])
walk(0,set(),[]);results.sort(key=lambda v:-v[0]);best=results[0][0] if results else None
out={'fixed_D':D,'fixed_B':B,'total':len(results),'max_squares':best,'witnesses':[{'A':[x[0]for x in p],'C':[x[1]for x in p],'mask':sum(int(x[2])<<i for i,x in enumerate(p))} for s,p in results if s==best][:20]}
Path('work/lanes/SOTA_RESOURCE_20261028/preserve_b_geometry.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
