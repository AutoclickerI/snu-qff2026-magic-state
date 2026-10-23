import itertools
cells=[(r,c) for r in range(6) for c in range(6)]
def adj(a,b):return abs(a[0]-b[0])+abs(a[1]-b[1])==1
D=[(0,0),(3,1),(1,1),(0,4),(0,3),(2,3),(1,2)]
W=[{0,2,4,6},{1,2,5,6},{3,4,5,6},{0,1,4,5},{0,2,3,5},{1,2,3,4},{0,1,3,6}]
for S in W:
 ds=[D[i] for i in sorted(S)]
 opts=[]
 for ms in itertools.product(*[[x for x in cells if adj(x,d)] for d in ds]):
  if len(set(ms))<4 or any(x in D for x in ms):continue
  # connected induced
  seen={0};changed=1
  while changed:
   changed=0
   for i in list(seen):
    for j in range(4):
     if j not in seen and adj(ms[i],ms[j]):seen.add(j);changed=1
  if len(seen)==4:opts.append(ms)
 print(sorted(S),'options',len(opts),'ex',opts[:4])
