import os,sys,json,argparse
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent
sys.path.insert(0,str(H.parent/'BC2'))
import sat6,ft
p=argparse.ArgumentParser();p.add_argument('layout');p.add_argument('--depth',type=int,default=22);p.add_argument('--seconds',type=float,default=240);p.add_argument('--rule',default='clean');p.add_argument('--out',required=True);a=p.parse_args()
d=json.loads(Path(a.layout).read_text());sat6.B=ft.B=d['b'];sat6.C=ft.C=d['c']
st,prep,wall,it,n=sat6.solve(a.depth,[],0,threads=1,rule=a.rule,seconds=a.seconds)
r=dict(status=st,wall=wall,iterations=it,fault_constraints=n,args=vars(a))
if prep:
 r['cx']=sum(map(len,prep['ops']));Path(a.out+'.prep.json').write_text(json.dumps(prep,indent=2)+'\n')
Path(a.out+'.receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
