"""Construct FT joint prep witnesses: independent staged encoders, then token swaps.
The returned ops can seed sat6 with an actual <=K bound. Every witness is checked
by ft.faults; no FT claim relies only on the construction argument.
"""
import sys,os
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,collections,subprocess,argparse,random
from pathlib import Path
import ft,exenc
ap=argparse.ArgumentParser();ap.add_argument('layout');ap.add_argument('--limit',type=int,default=0);ap.add_argument('--samples',type=int,default=1);a=ap.parse_args()
p=Path(a.layout).resolve();l=json.loads(p.read_text());cells=sorted(l['b']+l['c']);S=set(cells)
def nb(q):return [v for v in S if abs(q//6-v//6)+abs(q%6-v%6)==1]
edges=[(u,v) for u in cells for v in nb(u) if u<v]
ix={q:i for i,q in enumerate(cells)};full=(1<<14)-1
target=sum(1<<ix[q] for q in l['b']);dist={target:0};parent={};todo=collections.deque([target]);stages=[]
def connected(mask):
 nodes={q for q in cells if mask>>ix[q]&1};seen={next(iter(nodes))};todo=list(seen)
 for q in todo:
  for v in nb(q):
   if v in nodes and v not in seen:seen.add(v);todo.append(v)
 return seen==nodes
while todo:
 mask=todo.popleft()
 if connected(mask) and connected(mask^full):stages.append(mask)
 for u,v in edges:
  i,j=ix[u],ix[v]
  if (mask>>i&1)==(mask>>j&1):continue
  nxt=mask^(1<<i)^(1<<j)
  if nxt not in dist:dist[nxt]=dist[mask]+1;parent[nxt]=(mask,(u,v));todo.append(nxt)
print('stages',len(stages),'minswaps',min((dist[m] for m in stages),default=None),flush=True)
ft.B=l['b'];ft.C=l['c'];binary=exenc.compile_engine();front=[];cache={};rng=random.Random(412)
for num,mask in enumerate(stages*a.samples):
 if a.limit and num>=a.limit:break
 swaps=[];m=mask
 while m!=target:
  opts=[]
  for u,v in edges:
   nxt=m^(1<<ix[u])^(1<<ix[v])
   if nxt in dist and dist[nxt]==dist[m]-1:opts.append((nxt,(u,v)))
  m,e=rng.choice(opts);swaps.append(e)
 tokens={q:(k,i) for k in ('b','c') for i,q in enumerate(l[k])}
 for u,v in reversed(swaps):tokens[u],tokens[v]=tokens[v],tokens[u]
 stage={k:[next(q for q,t in tokens.items() if t==(k,i)) for i in range(7)] for k in ('b','c')}
 preps={}
 for k in ('b','c'):
  key=tuple(stage[k])
  if key not in cache:
   req=' '.join(map(str,[7,3,0,1,0,0,0,*stage[k]]))+'\n'
   r=subprocess.run([str(binary)],input=req,text=True,capture_output=True,check=True)
   prep=json.loads(r.stdout)['depth_optimal'];exenc.verify(prep,stage[k],'zero',[]);cache[key]=prep
  preps[k]=cache[key]
 linear=[e for k in ('b','c') for layer in preps[k]['ops'] for e in layer]
 for u,v in swaps:linear.extend([[u,v],[v,u],[u,v]])
 # Cancel adjacent identical CNOTs, including gates separated only by disjoint ops.
 kept=[];last={}
 for e in linear:
  u,v=e;j=last.get(u)
  if j is not None and j==last.get(v) and kept[j]==e:
   kept[j]=None
   for q in e:last[q]=next((i for i in range(j-1,-1,-1) if kept[i] and q in kept[i]),None)
  else:
   kept.append(e);last[u]=last[v]=len(kept)-1
 ops=[];last={}
 for e in kept:
  if e is None:continue
  t=max((last.get(q,-1) for q in e))+1
  while len(ops)<=t:ops.append([])
  ops[t].append(e)
  for q in e:last[q]=t
 d=dict(ops=ops,pivots=preps['b']['pivots']+preps['c']['pivots'],cx=sum(map(len,ops)),depth=len(ops),stage=stage,swaps=swaps,layout=p.name,method='staged independent encoders + token swaps')
 bad=ft.faults(d,cells)
 if bad:raise AssertionError(bad[:3])
 if any(c['cx']<=d['cx'] and c['depth']<=d['depth'] for c in front):continue
 front=[c for c in front if not(d['cx']<=c['cx'] and d['depth']<=c['depth'])]+[d]
 (p.with_name(p.stem+'_BC_construct.json')).write_text(json.dumps(front,indent=2)+'\n')
 print('WITNESS',num,'cx',d['cx'],'depth',d['depth'],'swaps',len(swaps),flush=True)
for j,d in enumerate(sorted(front,key=lambda d:(d['cx'],d['depth']))):
 p.with_name(p.stem+f'_BC_construct_{j}.json').write_text(json.dumps(d,indent=2)+'\n')
