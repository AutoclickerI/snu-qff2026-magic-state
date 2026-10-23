import itertools,random,sys,json
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/DR'); import relaxed
W=relaxed.W4; TR=relaxed.TRIPLES

def bip(edges):
 adj={}
 for a,b in edges:adj.setdefault(a,set()).add(b);adj.setdefault(b,set()).add(a)
 col={}
 for v in adj:
  if v in col:continue
  col[v]=0;st=[v]
  while st:
   a=st.pop()
   for z in adj[a]:
    if z in col:
     if col[z]==col[a]:return False
    else: col[z]=1-col[a];st.append(z)
 return True

def graph(xt,zt,modes,perms):
 edges=[];vn=7; checks=[('X',k) for k in xt]+[('Z',k) for k in zt]
 for ci,(typ,k) in enumerate(checks):
  ds=list(W[k]);p=perms[ci];m=list(range(vn,vn+4));vn+=4
  if modes[ci]=='pair':edges += [(m[0],ds[p[0]]),(m[0],ds[p[2]]),(m[1],ds[p[1]]),(m[1],ds[p[3]]),(m[0],m[1])]
  else:
   edges += [(m[i],ds[p[i]]) for i in range(4)]+[(m[0],m[1]),(m[1],m[2]),(m[2],m[3])]
   if modes[ci]=='clean':
    for i,j in enumerate([1,2,3,2]):w=vn;vn+=1;edges += [(m[i],w),(m[j],w)]
   elif modes[ci]=='cat1':w=vn;vn+=1;edges += [(m[0],w),(m[1],w)]
 return edges
for mode_name,modes in [('pair',['cat1']*3+['pair']*3),('hybcat',['cat1']*6),('clean',['clean']*6),('xcatzpair',['clean']*3+['pair']*3)]:
 print('MODE',mode_name,flush=True); found=0
 for ix in TR:
  for iz in TR:
   for trial in range(2000):
    perms=[random.sample(range(4),4) for _ in range(6)]
    if bip(graph(ix,iz,modes,perms)):
     print('FOUND',ix,iz,perms,flush=True);found=1;break
   if found:break
  if found:break
 print('count',found,flush=True)
