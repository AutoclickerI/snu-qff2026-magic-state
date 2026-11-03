import json,collections
from pathlib import Path
R=Path.cwd();H=R/'work/lanes/SOTA_RESOURCE_20261028';p=R/'work/lanes/NATIVE2_20261027/a_measured.json'
doc=json.loads(p.read_text());doc['prefix_stem']=str(R/'work/lanes/NATIVE2_20261027/boundary/source_prefix_d828869d5031c029_d6_20_19_10_2_22_16');(H/'a_module.json').write_text(json.dumps(doc,indent=2)+'\n')
D=[6,20,19,10,2,22,16];A=[7,14,18,4,8,21,15];B=[12,26,25,11,3,28,17];C=[13,27,24,5,9,29,23]
allowed=set(range(36))-set(D)
def path(a,b):
 prev={a:None};todo=collections.deque([a])
 while todo:
  q=todo.popleft()
  if q==b:break
  for r in sorted(allowed-prev.keys()):
   if abs(q//6-r//6)+abs(q%6-r%6)==1:prev[r]=q;todo.append(r)
 if b not in prev:raise ValueError((a,b))
 z=[]
 while b is not None:z.append(b);b=prev[b]
 return z[::-1]
def remote(p):
 if len(p)==2:return [p]
 edges=[[a,b] for a,b in zip(p,p[1:])];half=edges+edges[-2:0:-1];return half+half
logical=[]
for layer in [[(0,2),(1,5),(3,6)],[(0,4),(1,6),(3,5)],[(0,6),(1,2),(3,4)]]:
 logical += [(B[a],B[b]) for a,b in layer]
logical += [(C[0],C[3]),(C[0],C[4])]
logical += [(B[i],C[i]) for i in [0,2,3,4]]
ops=[];initial=set(B+C)-{C[i] for i in (1,5,6)}
for q in sorted(initial):ops.append(dict(kind='RX' if q in (B[0],B[1],B[3],C[0]) else 'R',qs=[q],time=46))
last={q:46 for q in allowed};last.update({q:46 for q in A})
for a,b in logical:
 for e in remote(path(a,b)):
  t=max(last[e[0]],last[e[1]])+1
  ops.append(dict(kind='CX',qs=e,time=t));last[e[0]]=last[e[1]]=t
end=max(last.values())
for i in (1,5,6):ops.append(dict(kind='RX',qs=[C[i]],time=end+1))
roles=dict(D=D,A=A,B=B,C=C)
bc=dict(prefix_stem=doc['prefix_stem'],roles=roles,square_mask=29,operations=ops)
(H/'construct_four_bc.json').write_text(json.dumps(bc,indent=2)+'\n')
print('cx',sum(x['kind']=='CX' for x in ops),'end',end,'logical',len(logical),'paths',[(x,path(*x)) for x in logical])
