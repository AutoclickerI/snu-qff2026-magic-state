import os,sys,itertools,json,subprocess
sys.dont_write_bytecode=True
from pathlib import Path
H=Path(__file__).resolve().parent
GENS=[[0,2,4,6],[1,2,5,6],[3,4,5,6]]
def normalize(s):
 s=list(s)
 mr=min(r for r,c in s);mc=min(c for r,c in s);return tuple(sorted((r-mr,c-mc)for r,c in s))
def variants(s):
 return [normalize([(r,c),(r,-c),(-r,c),(-r,-c),(c,r),(c,-r),(-c,r),(-c,-r)][k]for r,c in s)for k in range(8)]
def canon(s):return min(variants(s))
def rowkey(rows):
 rr=list(rows)
 for i in range(3):
  j=min(range(i,3),key=lambda j:(rr[j]&-rr[j]).bit_length());rr[i],rr[j]=rr[j],rr[i];b=rr[i]&-rr[i]
  for j in range(3):
   if j!=i and rr[j]&b:rr[j]^=rr[i]
 return sum(r<<(7*i)for i,r in enumerate(rr))
def generate():
 shapes={((0,0),)}
 for n in range(2,8):
  new=set()
  for s in shapes:
   for r,c in s:
    for x in ((r-1,c),(r+1,c),(r,c-1),(r,c+1)):
     if x not in s:new.add(canon(s+(x,)))
  shapes=new
 shapes=sorted(s for s in shapes if max(r for r,c in s)<6 and max(c for r,c in s)<6)
 embeddings=[]
 for sid,s in enumerate(shapes):
  seen=set()
  for k in range(8):
   # preserve native vertex indices across isometries
   a=[[(r,c),(r,-c),(-r,c),(-r,-c),(c,r),(c,-r),(-c,r),(-c,-r)][k]for r,c in s];mr=min(r for r,c in a);mc=min(c for r,c in a);a=[(r-mr,c-mc)for r,c in a]
   hh=max(r for r,c in a)+1;ww=max(c for r,c in a)+1
   for dr in range(7-hh):
    for dc in range(7-ww):seen.add(tuple((r+dr)*6+c+dc for r,c in a))
  embeddings.extend([sid,*s]for s in sorted(seen))
 targets={};perms=[]
 for p in itertools.permutations(range(7)):
  key=rowkey([sum(1<<p[i]for i in row)for row in GENS]);cid=targets.setdefault(key,len(targets));perms.append([cid,*p])
 info=dict(shapes=shapes,embeddings=embeddings,targets=list(targets),permutations=perms)
 (H/'library_input.json').write_text(json.dumps(info))
 lines=[f'{len(shapes)} {len(targets)}', ' '.join(map(str,targets))]
 for s in shapes:
  edges=[(i,j)for i in range(7)for j in range(7)if abs(s[i][0]-s[j][0])+abs(s[i][1]-s[j][1])==1]
  lines.append(str(len(edges))+' '+' '.join(str(x)for e in edges for x in e))
 (H/'library_input.txt').write_text('\n'.join(lines)+'\n')
 print(dict(shapes=len(shapes),embeddings=len(embeddings),label_classes=len(targets),permutations=len(perms)),flush=True)
if __name__=='__main__':generate()
