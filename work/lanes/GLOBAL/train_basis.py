"""Search an equivalent detector basis once and save it in a separate evaluator copy."""
import hashlib,json,shutil,sys,time
from pathlib import Path
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H/'sparse'))
import sparse_walsh as sw
stem=H/'builds'/sys.argv[1]
m,eng,groups,nd,ks,*_=sw.prepare(stem,True)
old=json.loads((H/'sparse/basis_warm.json').read_text());keys=[','.join(map(str,sorted(d))) for d in m.dets]
trials=int(sys.argv[2]) if len(sys.argv)>2 else 10000
options=[sw.search_basis(m,eng,groups,nd,set(ks),w,trials=0) for w in old['bases'].values()]
ops,cost=min(options,key=lambda r:r[1]);warm=[[keys[i],keys[j]] for i,j in ops]
before=cost;start=time.time()
for seed in [80353,90457]:
    op,co=sw.search_basis(m,eng,groups,nd,set(ks),warm,trials=trials,seed=seed)
    if co<cost:ops,cost=op,co;warm=[[keys[i],keys[j]] for i,j in ops]
    print(json.dumps(dict(seed=seed,cost=cost,seconds=time.time()-start)),flush=True)
fast=H/(sys.argv[3] if len(sys.argv)>3 else 'sparse_fast');fast.mkdir(exist_ok=True)
for f in ['sparse_walsh.py','frontend.py','fastfill.py']:shutil.copy2(H/'sparse'/f,fast/f)
shutil.copytree(H/'sparse/judge_subset',fast/'judge_subset',dirs_exist_ok=True)
old['bases']['GLOBAL_'+stem.name]=warm
(fast/'basis_warm.json').write_text(json.dumps(old,indent=2)+'\n')
(H/'logs'/f'{stem.name}.basis.json').write_text(json.dumps(dict(source=str(stem),sha256=hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest(),before=before,after=cost,seconds=time.time()-start,ops=warm),indent=2)+'\n')
