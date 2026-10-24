"""Exact graph-state LC / Pauli-measurement search. No external libraries."""
from itertools import combinations, permutations, product
from collections import deque, defaultdict
from pathlib import Path
import json

def graph(n, edges):
 a=[0]*n
 for u,v in edges:a[u]|=1<<v;a[v]|=1<<u
 return tuple(a)
def lc(a,v):
 b=list(a);ns=[j for j in range(len(a)) if a[v]>>j&1]
 for j,k in combinations(ns,2):b[j]^=1<<k;b[k]^=1<<j
 return tuple(b)
def delete(a,v):
 keep=[j for j in range(len(a)) if j!=v]
 return tuple(sum(((a[j]>>k)&1)<<i for i,k in enumerate(keep)) for j in keep)
def measure(a,v,basis):
 if basis=='Y':a=lc(a,v)
 if basis=='X' and a[v]:
  w=(a[v]&-a[v]).bit_length()-1
  a=lc(lc(lc(a,w),v),w)
 return delete(a,v)
def canon(a):
 groups=defaultdict(list)
 for j,row in enumerate(a):groups[row.bit_count()].append(j)
 choices=[list(permutations(groups[d])) for d in sorted(groups)]
 best=None;best_order=None
 for blocks in product(*choices):
  order=sum(blocks,())
  m=0;t=0
  for j in range(len(a)):
   for k in range(j):m|=((a[order[j]]>>order[k])&1)<<t;t+=1
  if best is None or m<best:best=m;best_order=order
 return best,best_order
def edges(a):return [(j,k) for j in range(len(a)) for k in range(j) if a[j]>>k&1]

target=graph(7,[(0,2),(0,4),(0,6),(1,2),(1,5),(1,6),(3,4),(3,5),(3,6)])
queue=deque([target]);seqs={target:()};classes={}
while queue:
 a=queue.popleft();ca,order=canon(a)
 classes.setdefault(ca,(a,seqs[a],order))
 for v in range(7):
  b=lc(a,v)
  if b not in seqs:seqs[b]=seqs[a]+(v,);queue.append(b)
grid=graph(9,[(r*3+c,(r+dr)*3+c+dc) for r in range(3) for c in range(3) for dr,dc in [(1,0),(0,1)] if r+dr<3 and c+dc<3])
witnesses=[]
for pair in combinations(range(9),2):
 for bases in product('XYZ',repeat=2):
  a=grid;remain=list(range(9))
  for v,basis in zip(pair,bases):
   pos=remain.index(v);a=measure(a,pos,basis);remain.pop(pos)
  ca,order=canon(a)
  if ca in classes:
   rep,seq,torder=classes[ca]
   witnesses.append(dict(measured=pair,bases=bases,remaining=remain,derived_graph=edges(a),target_lc_sequence=seq,measured_order=order,target_order=torder))
result=dict(target_graph_edges=edges(target),target_labelled_lc_orbit=len(seqs),target_unlabelled_lc_classes=len(classes),minimum_edges_in_target_lc_orbit=min(len(edges(a)) for a in seqs),cluster_3x3_witnesses=witnesses)
Path(__file__).with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:(len(v) if isinstance(v,list) and k=='cluster_3x3_witnesses' else v) for k,v in result.items()},indent=2))
