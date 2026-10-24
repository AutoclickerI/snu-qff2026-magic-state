import os,sys,json,itertools
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn');HERE=Path(__file__).parent;sys.path.insert(0,str(ROOT/'work'/'lanes'/'ST_BC'));import ft
orig={'b':[6,26,13,11,4,23,27],'c':[12,25,19,17,5,29,28]};chain=[6,12,13,19,25,26,27,28,29,23,17,11,5,4]
prep=json.loads((ROOT/'work/lanes/ST_BC/sat4_14_4.json').read_text());autos=[]
for v0,v1,v2 in itertools.permutations(range(1,8),3):
 im=[(v0 if n&1 else 0)^(v1 if n&2 else 0)^(v2 if n&4 else 0) for n in range(1,8)]
 if len(set(im))==7 and 0 not in im:autos.append(tuple(n-1 for n in im))
for f in sorted(HERE.glob('lay2_*.json')):
 l=json.loads(f.read_text());S=set(l['b']+l['c']);adj={q:[v for v in S if abs(q//6-v//6)+abs(q%6-v%6)==1] for q in S};paths=[]
 def rec(p):
  if len(p)==14:paths.append(p);return
  for v in adj[p[-1]]:
   if v not in p:rec(p+[v])
 for q in S:rec([q])
 found=0;ft.B=l['b'];ft.C=l['c']
 for path in paths:
  mp=dict(zip(chain,path));
  for swap in (False,True):
   for pb in autos:
    for pc in autos:
     # original role labels map to path cells; swap allows role interchanging only if geometry
     roleb=l['b'] if not swap else l['c'];rolec=l['c'] if not swap else l['b']
     mb={q:roleb[pb[i]] for i,q in enumerate(orig['b'])};mc={q:rolec[pc[i]] for i,q in enumerate(orig['c'])}
     mp2={**mb,**mc}
     ops=[[[mp2[u],mp2[v]] for u,v in layer] for layer in prep['ops']]
     if not all(abs(u//6-v//6)+abs(u%6-v%6)==1 for lay in ops for u,v in lay):continue
     d=dict(ops=ops,pivots=[mp2[q] for q in prep['pivots']],cx=sum(map(len,ops)),depth=len(ops),cap=80,source='ST_BC/sat4_14_4.json',permB=list(pb),permC=list(pc),swap=swap,layout=f.name)
     if ft.faults(d):continue
     out=HERE/(f.stem+'_BC_template.json');out.write_text(json.dumps(d,indent=2)+'\n');print('FOUND',f.name,'path',path,'swap',swap,'cx',d['cx']);found=1;break
    if found:break
   if found:break
  if found:break
 print(f.name,'paths',len(paths),'found',found)
