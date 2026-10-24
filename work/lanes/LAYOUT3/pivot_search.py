import os,sys,json,itertools,random,time
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
HERE=Path(__file__).parent;sys.path.insert(0,str(HERE));import sat6,ft
name=sys.argv[1];depth=int(sys.argv[2]);cap=int(sys.argv[3]);seconds=float(sys.argv[4]);l=json.loads((HERE/(name+'.json')).read_text());sat6.B=ft.B=l['b'];sat6.C=ft.C=l['c'];helpers=l.get('hBC',[])
# all row-compatible triples first, then random permutations
opts=list(itertools.permutations(range(7),3));rng=random.Random(0);rng.shuffle(opts)
bests=[];start=time.time();n=0
for ib in opts:
 for ic in opts:
  if time.time()-start>seconds:break
  piv=[l['b'][i] for i in ib]+[l['c'][i] for i in ic];n+=1
  st,d,el,it,nf=sat6.solve(depth,helpers,n,threads=1,K=cap,rule='clean',seconds=min(8,seconds-(time.time()-start)),pivfix=piv)
  if st=='SAT':
   d.update(layout=name,depth=depth,cap=cap,seed=n,rule='clean',pivfix=piv,cx=sum(map(len,d['ops'])));out=HERE/(name+'_BC_clean.json');out.write_text(json.dumps(d,indent=2)+'\n');print('SAT',n,ib,ic,d['cx'],flush=True);raise SystemExit
  if n%20==0:print('TRY',n,st,flush=True)
print('DONE',n,flush=True)
