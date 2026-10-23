"""Embed a proven BC path circuit, allowing <=2 final adjacent SWAPs (<=79 CX)."""
import os,sys,json,itertools
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import ft
here=Path(__file__).resolve().parent;orig={'b':[6,26,13,11,4,23,27],'c':[12,25,19,17,5,29,28]};chain=[6,12,13,19,25,26,27,28,29,23,17,11,5,4]
prep=json.loads((here.parent/'ST_BC/sat4_14_4.json').read_text());autos=set()
for v0,v1,v2 in itertools.permutations(range(1,8),3):
 im=[(v0 if n&1 else 0)^(v1 if n&2 else 0)^(v2 if n&4 else 0) for n in range(1,8)]
 if len(set(im))==7 and 0 not in im:autos.add(tuple(n-1 for n in im))
seen=set()
for f in here.glob('*.json'):
 try:l=json.loads(f.read_text())
 except ValueError:continue
 if not isinstance(l,dict) or not all(k in l for k in ('a','b','c','d','M','moves')):continue
 key=(tuple(l['b']),tuple(l['c']))
 if key in seen:continue
 seen.add(key);S=set(l['b']+l['c']);nb={q:[v for v in S if abs(q//6-v//6)+abs(q%6-v%6)==1] for q in S}
 paths=[]
 def rec(path):
  if len(path)==14:paths.append(path);return
  for v in nb[path[-1]]:
   if v not in path:rec(path+[v])
 for q in S:rec([q])
 es=[(q,v) for q in S for v in nb[q] if q<v];swseq=[()]+[(e,) for e in es]+list(itertools.product(es,repeat=2))
 ft.B=l['b'];ft.C=l['c'];final={q:(k,i) for k in 'bc' for i,q in enumerate(l[k])};n=0
 for path in paths:
  mp=dict(zip(chain,path))
  for swaps in swseq:
   tokens=final.copy()
   for u,v in reversed(swaps):tokens[u],tokens[v]=tokens[v],tokens[u]
   roles={k:{tokens[mp[q]][0] for q in orig[k]} for k in 'bc'}
   if any(len(v)!=1 for v in roles.values()) or roles['b']==roles['c']:continue
   perms={k:tuple(tokens[mp[q]][1] for q in orig[k]) for k in 'bc'}
   if any(v not in autos for v in perms.values()):continue
   flat=[[mp[u],mp[v]] for layer in prep['ops'] for u,v in layer]
   for u,v in swaps:flat.extend([[u,v],[v,u],[u,v]])
   ops=[];last={}
   for e in flat:
    t=max(last.get(q,-1) for q in e)+1
    while len(ops)<=t:ops.append([])
    ops[t].append(e)
    for q in e:last[q]=t
   d=dict(ops=ops,pivots=[mp[q] for q in prep['pivots']],cx=sum(map(len,ops)),depth=len(ops),cap=80,source='ST_BC/sat4_14_4.json',swaps=swaps,layout=f.name)
   if ft.faults(d):continue
   out=f.with_name(f.stem+f'_BC_sw{n}.json');out.write_text(json.dumps(d,indent=2)+'\n');print('SWAP_TEMPLATE',f.name,n,d['cx'],d['depth'],swaps,flush=True);n+=1
