import itertools,random,time
cells=[(r,c) for r in range(6) for c in range(6)]
adj=lambda a,b:abs(a[0]-b[0])+abs(a[1]-b[1])==1
W=[{0,2,4,6},{1,2,5,6},{3,4,5,6},{0,1,4,5},{0,2,3,5},{1,2,3,4},{0,1,3,6}]
# cache support local by tuple data cells
def opts(ds):
 out=[]
 for ms in itertools.product(*[[x for x in cells if adj(x,d)] for d in ds]):
  if len(set(ms))<4 or any(x in ds for x in ms):continue
  seen={0}; ch=1
  while ch:
   ch=0
   for i in list(seen):
    for j in range(4):
     if j not in seen and adj(ms[i],ms[j]):seen.add(j);ch=1
  if len(seen)==4:out.append(ms)
 return out
def score(D):return sum(bool(opts([D[i] for i in sorted(S)])) for S in W)
best=(0,None);t0=time.time()
for restart in range(500):
 D=random.sample(cells,7);cur=score(D)
 for it in range(10000):
  i=random.randrange(7); old=D[i]; x=random.choice([z for z in cells if z not in D]);D[i]=x;v=score(D)
  T=max(.02,1.2*(1-it/10000))
  if v>=cur or random.random()<pow(2.71828,(v-cur)/T):cur=v
  else:D[i]=old
  if cur>best[0]:
   best=(cur,D[:]);print('best',cur,best[1],time.time()-t0,flush=True)
   if cur==7:
    for S in W:print(sorted(S),opts([D[i] for i in sorted(S)])[0])
    raise SystemExit
print('FINAL',best)
