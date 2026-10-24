from common import *
import itertools
perms=[]
for a,b,c in itertools.product(range(1,8),repeat=3):
 p=[((a if i&1 else 0)^(b if i&2 else 0)^(c if i&4 else 0))-1 for i in range(1,8)]
 if sorted(p)==list(range(7)):perms.append(p)
cs=json.loads((HERE/'encoder_candidates.json').read_text());seen=set();maps=[];new=[]
def key(c):
 edges=[tuple(e) for L in c['ops'] for e in L]
 return (tuple(sorted(c['pivots'])),tuple(tuple(e for e in edges if q in e) for q in A))
seen={key(c) for c in cs}
for ci,c in enumerate(cs):
 for p in perms:
  mp={A[i]:A[p[i]] for i in range(7)}
  if any(abs(mp[u]//6-mp[v]//6)+abs(mp[u]%6-mp[v]%6)!=1 for L in c['ops'] for u,v in L):continue
  cc=dict(ops=[[[mp[u],mp[v]] for u,v in L] for L in c['ops']],pivots=[mp[q] for q in c['pivots']],origin=ci,perm=p)
  maps.append([ci,p]);k=key(cc)
  if k not in seen:seen.add(k);new.append(cc)
# A code relabeling changes which physical support is desired; it cannot
# create a physical neighbour shared by a line where none exists.
lines=[comb for comb in itertools.combinations(range(7),3) if (comb[0]+1)^(comb[1]+1)^(comb[2]+1)==0]
stars=[]
for g in lines:
 cells=[A[i] for i in g]
 nbr=[q for q in range(36) if all(abs(q//6-v//6)+abs(q%6-v%6)==1 for v in cells)]
 stars.append(dict(line=g,cells=cells,common_neighbours=nbr))
(HERE/'automorphism_audit.json').write_text(json.dumps(dict(permutations=len(perms),legal_embeddings=len(maps),distinct_new=len(new),lines=stars,new=new),indent=1))
print('automorphisms',len(perms),'legal embeddings',len(maps),'new',len(new),'stars',stars,flush=True)
