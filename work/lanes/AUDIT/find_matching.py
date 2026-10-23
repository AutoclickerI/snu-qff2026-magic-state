from random import sample, seed
N=36; SUP=[{0,2,4,6},{1,2,5,6},{3,4,5,6}]; req=[i for P in range(2) for s in SUP for i in sorted(s)]
def match(data):
  allowed=[]
  for r in req:
    a=data[r]; allowed.append([q for q in range(N) if q not in data and abs(q//6-a//6)+abs(q%6-a%6)==1])
  mr=[-1]*N; rr=[-1]*24
  def dfs(r,seen):
    for q in allowed[r]:
      if seen>>q&1: continue
      seen |= 1<<q
      if mr[q]<0 or dfs(mr[q],seen): mr[q]=r; rr[r]=q; return True
    return False
  n=0
  for r in sorted(range(24),key=lambda r:len(allowed[r])):
    if dfs(r,0): n+=1
  return n,rr
seed(0); best=(0,None,None)
for t in range(200000):
 data=sample(range(N),7); n,x=match(data)
 if n>best[0]: best=(n,sorted(data),x); print('best',best,flush=True)
 if n==24: break
print('final',best)
