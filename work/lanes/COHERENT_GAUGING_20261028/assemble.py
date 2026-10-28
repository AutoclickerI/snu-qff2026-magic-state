"""Complete native seed + flagged coherent gauging + optional IBM syndrome rounds.
Gauge recovery uses fused tree identity; every physical operation remains noisy.
"""
import os
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,collections
from pathlib import Path
H=Path(__file__).resolve().parent;R=H.parents[2]
sys.path[:0]=[str(H),str(R/'work/lanes/FRAME20261027'),str(R/'work/lanes/EXPAND2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
import frontend_axis as f,frame_tools as ft,record_contract,stab
from qtools.evaluator import sparse_walsh as sw
ft.f=f;record_contract.fa=f;sw.fa=f;sw.parse_current=f.parse_current;ft.OUT=H
D=[0,11,9,26,12,21,14];V=[0,2,9,11,12,14,21,23,24,26];E=[1,3,6,8,10,13,15,17,18,20,22,25];F=[7,16,19];boundary=[2,23,24];f.DATA=D
links=[(0,2,1),(9,2,3),(12,0,6),(9,14,8),(9,11,10),(12,14,13),(21,14,15),(23,11,17),(24,12,18),(21,26,20),(21,23,22),(24,26,25)]
flag_edges=[(7,1),(7,6),(7,8),(16,10),(16,15),(16,17),(19,13),(19,18),(19,20)]

def color(edges):
 remaining=sorted(edges,key=lambda e:-(sum(e[0] in x or e[1] in x for x in edges)))
 colors=[[],[],[]]
 def go(i):
  if i==len(remaining):return True
  a,b=remaining[i]
  for layer in colors:
   if all(a not in e and b not in e for e in layer):
    layer.append((a,b))
    if go(i+1):return True
    layer.pop()
  return False
 assert go(0);return colors
G=color([(u,e)for u,v,e in links]+[(v,e)for u,v,e in links]+flag_edges)
flaglayers=color(flag_edges)
adj=collections.defaultdict(list)
for u,v,e in links:adj[u].append((v,e));adj[v].append((u,e))
parent={0:None};dq=collections.deque([0]);tree=[]
while dq:
 u=dq.popleft()
 for v,e in adj[u]:
  if v in parent:continue
  parent[v]=u;tree.append((u,v,e));dq.append(v)
assert len(tree)==9
used={e for _,_,e in tree};chords=[(u,v,e)for u,v,e in links if e not in used]

def gauge(ops,t,bit):
 ops += [f.Op('R',(q,),t)for q in E]+[f.Op('RX',(q,),t)for q in F+boundary];t+=1
 for layer in G:
  ops += [f.Op('CX',edge,t)for edge in layer];t+=1
 ops += [f.Op('T',(q,),t)for q in D];t+=1
 databits={q:bit+i for i,q in enumerate(V)}
 ops += [f.Op('MX',(q,),t,databits[q])for q in V];bit+=len(V);t+=1
 # Flag uncompute precedes every tree edge->child action.
 for layer in flaglayers:
  if layer:ops += [f.Op('CX',edge,t)for edge in layer];t+=1
 flagbits={q:bit+i for i,q in enumerate(F)};ops += [f.Op('MX',(q,),t,flagbits[q])for q in F];bit+=3;t+=1
 # Precompute child contribution on all edges before any vertex changes.
 for layer in color([(v,e) for u,v,e in tree]):
  if layer:ops += [f.Op('CX',edge,t)for edge in layer];t+=1
 # Parent is live before A and child is updated after C. ASAP on shared wires.
 ready={q:t for q in V+E}
 for u,v,e in tree:
  z=max(ready[u],ready[e]);ops.append(f.Op('CX',(u,e),z));ready[u]=ready[e]=z+1
  z=max(ready[e],ready[v]);ops.append(f.Op('CX',(e,v),z));ready[e]=ready[v]=z+1
 t=max(ready.values())
 # Non-tree chord becomes a cycle syndrome after both endpoint updates.
 for u,v,e in chords:
  z=max(ready[u],ready[v],ready[e]);ops.append(f.Op('CX',(u,e),z));ready[u]=ready[e]=z+1
  z=max(ready[v],ready[e]);ops.append(f.Op('CX',(v,e),z));ready[v]=ready[e]=z+1
 t=max(ready.values());ops += [f.Op('TDG',(q,),t)for q in D];t+=1
 ebits={q:bit+i for i,q in enumerate(E)};ops += [f.Op('M',(q,),t,ebits[q])for q in E];bit+=len(E)
 bbits={q:bit+i for i,q in enumerate(boundary)};ops += [f.Op('MX',(q,),t,bbits[q])for q in boundary];bit+=3;t+=1
 details={'data_bits':databits,'edge_bits':ebits,'flag_bits':flagbits,'boundary_bits':bbits,'tree':tree,'chords':chords,'G1_layers':G,'flags_layers':flaglayers,'end_time':t}
 return ops,t,bit,details

def run(mode):
 seed=H/'seed_t';ops,dets=f.parse_current(seed.with_suffix('.qasm').read_text());t=18;bit=4
 if mode in ('pre','both'):ops,dets,t,bit=stab.append_stab(ops,dets,t,bit)
 ops,t,bit,details=gauge(ops,t,bit)
 if mode in ('post','both'):ops,dets,t,bit=stab.append_stab(ops,dets,t,bit)
 ops.sort(key=lambda o:o.time)
 # Check every physical clock and edge before deriving records.
 used=set()
 for o in ops:
  for q in o.qs:
   if (o.time,q) in used:raise ValueError(('collision',o.time,o.kind,o.qs))
   used.add((o.time,q))
  if o.kind=='CX':
   a,b=o.qs;assert abs(a//6-b//6)+abs(a%6-b%6)==1,(o.time,o.qs)
 f.DATA=D;completion=record_contract.complete(f.make_model(ops,[]),[])
 negative=[r for r in completion['missing'] if r['reference']]
 if negative:
  print('NEGATIVE',json.dumps(negative),flush=True);return
 ds=[set(r['bits']) for r in completion['missing']]
 stem=ft.emit(f'full_{mode}',ops,ds,D,metadata={'scope':'complete noisy native 6x6','mode':mode,'gauge':details,'derived_contract_rows':len(ds)})
 raw=ft.raw_check(stem.with_suffix('.qasm').read_text(),D)
 print('RAW',json.dumps({'mode':mode,'raw':raw,'ticks':t,'T':sum(o.kind in ('T','TDG')for o in ops),'cx':sum(o.kind=='CX'for o in ops),'rows':len(ds),'gauge':details}),flush=True)
 if raw['ok']:
  sg=ft.singles(stem);print('SINGLES',json.dumps({'loss':sg['first_order_loss'],'n':sg['harmful_count']}),flush=True)
  print('PRICE',json.dumps(ft.price(stem)),flush=True)
if __name__=='__main__':run(sys.argv[1] if len(sys.argv)>1 else 'none')
