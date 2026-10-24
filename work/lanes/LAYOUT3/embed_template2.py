import os,sys,json,itertools
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn');HERE=Path(__file__).parent;sys.path.insert(0,str(ROOT/'work'/'lanes'/'BC2'));import ft
orig={'b':[6,26,13,11,4,23,27],'c':[12,25,19,17,5,29,28]};chain=[6,12,13,19,25,26,27,28,29,23,17,11,5,4];prep=json.loads((ROOT/'work'/'lanes'/'ST_BC'/'sat4_14_4.json').read_text());autos=set()
for v0,v1,v2 in itertools.permutations(range(1,8),3):
 im=[(v0 if n&1 else 0)^(v1 if n&2 else 0)^(v2 if n&4 else 0) for n in range(1,8)]
 if len(set(im))==7 and 0 not in im:autos.add(tuple(n-1 for n in im))
for f in sorted(HERE.glob('lay2_*.json')):
 try:l=json.loads(f.read_text())
 except:continue
 if 'b' not in l:continue
 S=set(l['b']+l['c']);adj={q:[v for v in S if abs(q//6-v//6)+abs(q%6-v%6)==1] for q in S};paths=[]
 def rec(path):
  if len(path)==14:paths.append(path);return
  for v in adj[path[-1]]:
   if v not in path:rec(path+[v])
 for q in S:rec([q])
 found=False
 for path in paths:
  mp=dict(zip(chain,path));final={q:(k,i) for k in 'bc' for i,q in enumerate(l[k])}
  edges=[(u,v) for u in S for v in adj[u] if u<v]
  for swaps in [[]]+[[e] for e in edges]+[list(es) for es in itertools.combinations(edges,2)]:
   tokens=final.copy()
   for u,v in reversed(swaps):tokens[u],tokens[v]=tokens[v],tokens[u]
   roles={k:{tokens[mp[q]][0] for q in orig[k]} for k in 'bc'}
   if any(len(v)!=1 for v in roles.values()) or roles['b']==roles['c']:continue
   perms={k:tuple(tokens[mp[q]][1] for q in orig[k]) for k in 'bc'}
   if any(v not in autos for v in perms.values()):continue
   ops=[]
   for layer in prep['ops']:
    ops.append([[mp[u],mp[v]] for u,v in layer])
   for u,v in swaps:ops += [[u,v],[v,u],[u,v]]
   # schedule flat sequence into layers
   sched=[];last={}
   for e in [e for L in ops for e in L]:
    t=max(last.get(q,-1) for q in e)+1
    while len(sched)<=t:sched.append([])
    sched[t].append(e)
    for q in e:last[q]=t
   d=dict(ops=sched,pivots=[mp[q] for q in prep['pivots']],cx=sum(map(len,sched)),depth=len(sched),cap=100,source='ST_BC/sat4_14_4.json',swaps=swaps,layout=f.name)
   ft.B=l['b'];ft.C=l['c']
   if ft.faults(d):continue
   out=HERE/(f.stem+'_BC_template.json');out.write_text(json.dumps(d,indent=2)+'\n');print('FOUND',f.name,'path',path,'swaps',swaps,'cx',d['cx']);found=True;break
  if found:break
 print(f.name,'paths',len(paths),'found',found,flush=True)
