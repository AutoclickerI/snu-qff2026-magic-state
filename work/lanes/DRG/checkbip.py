import sys,json
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/DR'); import poc
s={int(k):[(t,typ,frozenset(S)) for t,typ,S in v] for k,v in json.load(open('/home/jihoon/competitions/quantumn/work/lanes/DR/sched_zfirst.json')).items()}
# build variants then filter op sets
for desc, bfn in [('baseverify',lambda:poc.build(s,verify=True)),('baseplain',lambda:poc.build(s,verify=False)),('cleanZfalse',lambda:poc.build_clean(s,clean_z=False)),('hybpair',lambda:poc.build_hybrid(s,z_mode='pair')),('hybcat1',lambda:poc.build_hybrid(s,z_mode='cat1')),('clean',lambda:poc.build_clean(s,clean_z=True))]:
 try:b,_,_=bfn()
 except Exception as e:print(desc,e);continue
 E=set(tuple(qs) for t,k,kind,qs,tag in b.ops if kind=='cx');adj={}
 for a,c in E:adj.setdefault(a,set()).add(c);adj.setdefault(c,set()).add(a)
 col={};bad=None
 for v in adj:
  if v in col:continue
  col[v]=0;st=[v]
  while st and bad is None:
   a=st.pop()
   for z in adj[a]:
    if z in col:
     if col[z]==col[a]:bad=(a,z);break
    else:col[z]=1-col[a];st.append(z)
 print(desc,'q',b.next_q,'E',len(E),'bip',bad is None,'bad',bad)
