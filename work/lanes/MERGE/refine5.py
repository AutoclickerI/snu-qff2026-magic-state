"""Independent exact detector-basis optimization; never mutates a running evaluator."""
from pass5 import *
import random
cur=json.loads((R/'wide_history.json').read_text())[-1]['price'];st=Path(cur['stem']);source=R/('basis_'+sha(st)+'.json');E.configure(source,12);sw=E.sw
with contextlib.redirect_stdout(io.StringIO()):m,eng,groups,nd,ks,*_=sw.prepare(st,True)
bases=json.loads(source.read_text());choices=[]
for name,warm in bases['bases'].items():
 ops,cost=sw.search_basis(m,eng,groups,nd,set(ks),warm,trials=0);choices.append((cost,ops,warm))
before,ops,warm=min(choices);keys=[','.join(map(str,sorted(d)))for d in m.dets];free=[i for i in range(nd)if i not in ks and tuple(eng.projs[i])==(0,0,1)and int(eng.v[i])==0];best=before;records=[]
for seed,n in [(73021,2),(73031,4),(73037,8),(73043,2)]:
 rng=random.Random(seed);w=list(warm)
 for _ in range(n):i,j=rng.sample(free,2);w.append([keys[i],keys[j]])
 t=time.monotonic();new,cost=sw.search_basis(m,eng,groups,nd,set(ks),w,trials=6000,seed=seed);records.append(dict(seed=seed,cost=cost,seconds=time.monotonic()-t))
 if cost<best:best=cost;ops=new;warm=[[keys[t],keys[j]]for t,j in new]
 print(json.dumps(dict(event='basis_refine',cost=cost,best=best,seed=seed)),flush=True)
bases['bases']['MERGE5_refine_'+sha(st)[:12]]=[[keys[t],keys[j]]for t,j in ops];target=R/('basis_refined_'+sha(st)+'.json');dump(target,bases);E.configure(target,12)
r=record(st,'independent basis refinement control',cur['loss']);assert abs(r['loss']-cur['loss'])<1e-13 and abs(r['acceptance']-cur['acceptance'])<1e-13
out=dict(before=before,after=best,records=records,price=r,source=str(source),target=str(target));dump(R/'basis_refinement5.json',out);print(json.dumps(dict(event='basis_refine_complete',before=before,after=best,seconds=r['seconds'])),flush=True)
