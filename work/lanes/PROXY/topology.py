"""Exhaustive local Bell-pair support availability, before schedule search."""
import sys,json,itertools
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn');HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'work'),str(ROOT/'work/lanes/me_layout')]
import gmodel as G
DATA=[G.P(q) for q in G.DATA0]
SUP=[frozenset(s) for s in G.PLAQ]
W4=[]
for bits in range(1,8):
 s=frozenset()
 for j in range(3):
  if bits>>j&1:s^=SUP[j]
 W4.append(s)
TRIPLES=[t for t in itertools.combinations(range(7),3) if W4[t[0]]^W4[t[1]]!=W4[t[2]]]
def adj(a,b):return abs(a%6-b%6)+abs(a//6-b//6)==1
E=[(a,b) for a in range(36) for b in range(a+1,36) if adj(a,b)]
def run(pos):
 free=set(range(36))-set(pos);edges=[e for e in E if set(e)<=free]
 # Every Z coupling must touch a Bell member. X may use a one-hop leaf.
 direct={e:frozenset(i for i,q in enumerate(pos) if any(adj(q,r) for r in e)) for e in edges}
 reach={e:frozenset(i for i,q in enumerate(pos) if any(adj(q,r) for r in e) or any(adj(q,c) and any(adj(c,r) for r in e) for c in free-set(e))) for e in edges}
 opts={(x,z):[e for e in edges if W4[z]<=direct[e] and W4[x]<=reach[e]] for x in range(7) for z in range(7)}
 survivors=[];direct_pairs=[]
 for xt in TRIPLES:
  for zt in TRIPLES:
   ways=[]
   for zp in itertools.permutations(zt):
    for es in itertools.product(*(opts[x,z] for x,z in zip(xt,zp))):
     if len(set(sum((list(e) for e in es),[])))<6:continue
     occupied=set(pos)|set(sum((list(e) for e in es),[]));leaves=[];ok=True
     for x,e in zip(xt,es):
      needs=[i for i in W4[x] if i not in direct[e]]
      for i in needs:
       optsleaf=[(c,r) for c in range(36) if c not in occupied for r in e if adj(pos[i],c) and adj(c,r)]
       if not optsleaf:ok=False;break
       leaves.append((i,optsleaf))
     if ok:ways.append(dict(xt=xt,zt=zp,bells=es,leaves=leaves))
   if ways:survivors.append(dict(xt=xt,zt=zt,ways=ways))
 return dict(data=pos,adjacent_edges=len(edges),per_support_z={str(k):[list(e) for e in edges if W4[k]<=direct[e]] for k in range(7)},surviving_pairs=len(survivors),survivors=survivors)
if __name__=='__main__':
 pos1=DATA.copy();pos1[1]=19
 r=dict(data_indices=DATA,W4=[sorted(s) for s in W4],triples=TRIPLES,total_pairs=len(TRIPLES)**2,original=run(DATA),A1=run(pos1))
 (HERE/'topology.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
