import os,sys,json,time
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
ROOT=Path('/home/jihoon/competitions/quantumn');HERE=Path(__file__).parent
sys.path.insert(0,str(HERE));import sat6,ft
name=sys.argv[1]; depth=int(sys.argv[2]); cap=int(sys.argv[3]); seconds=float(sys.argv[4]); seed=int(sys.argv[5])
l=json.loads((HERE/(name+'.json')).read_text());sat6.B=ft.B=l['b'];sat6.C=ft.C=l['c']
pivfix=[l['b'][i] for i in (0,1,3)]+[l['c'][i] for i in (0,1,3)]
st,d,elapsed,iters,nfaults=sat6.solve(depth,[],seed,threads=1,K=cap,rule='clean',seconds=seconds,pivfix=pivfix)
rec=dict(layout=name,depth=depth,cap=cap,seed=seed,status=st,elapsed=elapsed,iters=iters,constraints=nfaults)
if d:
 d.update(layout=name,depth=depth,cap=cap,seed=seed,rule='clean',cx=sum(map(len,d['ops'])));rec['cx']=d['cx'];(HERE/(name+'_BC_clean.json')).write_text(json.dumps(d,indent=2)+'\n')
(HERE/(name+'_BC_clean.receipt.json')).write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec),flush=True)
