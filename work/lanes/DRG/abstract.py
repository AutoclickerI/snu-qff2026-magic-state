import sys,json
sys.path.insert(0,'/home/jihoon/competitions/quantumn/work/lanes/DR'); import poc
s={int(k):[(t,typ,frozenset(S)) for t,typ,S in v] for k,v in json.load(open('/home/jihoon/competitions/quantumn/work/lanes/DR/sched_zfirst.json')).items()}
# graph based on built hybrid cat1 but remove verifier edge (v,m1), add v,m2
b,_,_=poc.build_hybrid(s,z_mode='cat1'); E=[]
for t,k,kind,qs,tag in b.ops:
 if kind!='cx':continue
 if tag is None:E.append(tuple(qs));continue
 # verifier tag absent on cx, identify verifier qubit by q >=? inspect all ops and tags impossible
 E.append(tuple(qs))
# identify triangles and print
adj={}
for a,c in E:adj.setdefault(a,set()).add(c);adj.setdefault(c,set()).add(a)
tri=[]
for a in adj:
 for b in adj[a]:
  for c in adj[b]:
   if c in adj[a]:tri.append(tuple(sorted((a,b,c))))
print('triangles',sorted(set(tri))[:30],len(set(tri)))
# locate each cat's verifier from tag and op sequence: verifier tag is op M/MX; preceding cx on same q
# identify all q with ver tag and two cx; remove edge to second member (likely m1), add m2? Determine member order via cat coupling times
for (typ,S),tags in []:pass
