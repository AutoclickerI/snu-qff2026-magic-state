import os,sys,json,itertools
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn');HERE=Path(__file__).parent;sys.path.insert(0,str(HERE));import ft
orig={'b':[6,26,13,11,4,23,27],'c':[12,25,19,17,5,29,28]};prep=json.loads((ROOT/'work/lanes/BC2/compact_clean_d14_k100.prep.json').read_text());autos=[]
for v0,v1,v2 in itertools.permutations(range(1,8),3):
 im=[(v0 if n&1 else 0)^(v1 if n&2 else 0)^(v2 if n&4 else 0) for n in range(1,8)]
 if len(set(im))==7 and 0 not in im:autos.append(tuple(n-1 for n in im))
for f in sorted(HERE.glob('lay2_*.json')):
 try:l=json.loads(f.read_text())
 except:continue
 if 'b' not in l:continue
 ft.B=l['b'];ft.C=l['c'];found=False
 for swap in (False,True):
  rb=l['c'] if swap else l['b'];rc=l['b'] if swap else l['c']
  for pb in autos:
   for pc in autos:
    mp={q:rb[pb[i]] for i,q in enumerate(orig['b'])};mp.update({q:rc[pc[i]] for i,q in enumerate(orig['c'])})
    ops=[[[mp[u],mp[v]] for u,v in L] for L in prep['ops']]
    if not all(abs(u//6-v//6)+abs(u%6-v%6)==1 for L in ops for u,v in L):continue
    d=dict(ops=ops,pivots=[mp[q] for q in prep['pivots']],cx=sum(map(len,ops)),depth=len(ops),cap=100,rule='clean',source='BC2/compact_clean_d14_k100.prep.json',permB=list(pb),permC=list(pc),swap=swap,layout=f.name)
    bad=ft.faults(d)
    if bad:continue
    (HERE/(f.stem+'_BC_clean.json')).write_text(json.dumps(d,indent=2)+'\n');print('FOUND',f.name,'swap',swap,'pb',pb,'pc',pc,'cx',d['cx']);found=True;break
   if found:break
  if found:break
 print(f.name,'found',found,flush=True)
