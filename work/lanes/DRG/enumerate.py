import sys,itertools,json
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/DR'); import poc,relaxed
W=relaxed.W4; TR=relaxed.TRIPLES

def bip(b):
 E=set(tuple(qs) for t,k,kind,qs,tag in b.ops if kind=='cx'); adj={}
 for a,c in E:adj.setdefault(a,set()).add(c);adj.setdefault(c,set()).add(a)
 col={}
 for v in adj:
  if v in col:continue
  col[v]=0;st=[v]
  while st:
   a=st.pop()
   for z in adj[a]:
    if z in col:
     if col[z]==col[a]:return False
    else:col[z]=1-col[a];st.append(z)
 return True
# schedule each support checks at arbitrary ranks preserving X/Z by index
cnt={x:0 for x in range(7)}
for ix in TR:
 for iz in TR:
  s={d:[] for d in range(7)}
  for typ,tr in [('X',ix),('Z',iz)]:
   for k in tr:
    for d in W[k]:s[d].append((len(s[d]),typ,W[k]))
  s={d:sorted(v) for d,v in s.items()}
  for name,fn in [('base',lambda:poc.build(s,verify=True)),('clean',lambda:poc.build_clean(s,clean_z=True)),('hyb',lambda:poc.build_hybrid(s,z_mode='cat1'))]:
   try:b,_,_=fn()
   except:continue
   if bip(b): print(name,ix,iz); break
