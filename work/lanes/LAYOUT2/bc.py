import sys,os
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,argparse,time,random
from pathlib import Path
import sat6,ft
ap=argparse.ArgumentParser();ap.add_argument('layout');ap.add_argument('depth',type=int);ap.add_argument('cap',type=int);ap.add_argument('seed',type=int);a=ap.parse_args()
p=Path(a.layout).resolve();l=json.loads(p.read_text());sat6.B=ft.B=l['b'];sat6.C=ft.C=l['c']
pf=bf=None
if os.environ.get('BC_PIVOTS'):
 cells=l['b']+l['c']+l['hBC']
 if a.seed:random.Random(a.seed).shuffle(cells)
 canonical=[l[k][i] for k in ('b','c') for i in (0,1,3)]
 pf=sorted(canonical,key=cells.index)
 if os.environ.get('BC_BASIS'):bf=[canonical.index(q) for q in pf]
start=time.time();r=sat6.solve(a.depth,l['hBC'],a.seed,threads=1,K=a.cap,pivfix=pf,basisfix=bf)
if r:
 ops,piv=r;d={'ops':ops,'pivots':piv,'cx':sum(map(len,ops)),'depth':len(ops),'cap':a.cap,'layout':p.name,'seed':a.seed,'seconds':time.time()-start}
 assert d['cx']<=a.cap
 assert not ft.faults(d,l['b']+l['c']+l['hBC'])
 vals={q:0 for q in l['b']+l['c']+l['hBC']}
 for j,q in enumerate(piv):vals[q]=1<<j
 for layer in ops:
  assert len({q for e in layer for q in e})==2*len(layer)
  for u,v in layer:assert v in sat6.nb(u);vals[v]^=vals[u]
 def rank(vs):
  basis={}
  for v in vs:
   while v:
    b=v.bit_length()-1
    if b not in basis:basis[b]=v;break
    v^=basis[b]
  return len(basis)
 cols=[sum(1<<q for q,v in vals.items() if v>>j&1) for j in range(6)]
 target=[sum(1<<blk[i] for i in row) for blk in (l['b'],l['c']) for row in sat6.ROWS]
 assert rank(cols)==rank(cols+target)==6 and all(vals[q]==0 for q in l['hBC'])
 out=p.with_name(f'{p.stem}_BC_d{a.depth}_k{a.cap}_s{a.seed}.json');out.write_text(json.dumps(d,indent=2)+'\n');print('VALIDATED',out.name,d['cx'],flush=True)
