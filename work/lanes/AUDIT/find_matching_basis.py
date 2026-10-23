from random import sample,seed
N=36; SUP=[{0,2,4,6},{1,2,5,6},{3,4,5,6}]; req=[i for s in SUP for i in sorted(s)]
def match(data):
 al=[]
 for r in req:
  a=data[r]; al.append([q for q in range(N) if q not in data and abs(q//6-a//6)+abs(q%6-a%6)==1])
 mr=[-1]*N; rr=[-1]*len(req)
 def dfs(r,seen):
  for q in al[r]:
   if seen>>q&1: continue
   seen|=1<<q
   if mr[q]<0 or dfs(mr[q],seen): mr[q]=r; rr[r]=q; return 1
  return 0
 return rr if all(dfs(r,0) for r in sorted(range(len(req)),key=lambda r:len(al[r]))) else None
seed(0)
for t in range(100000):
 data=sample(range(N),7); x=match(data)
 if x: print(t,sorted(data),x);break
