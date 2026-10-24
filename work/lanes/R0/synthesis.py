import os,sys,json,argparse,time
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import sat6,ft
p=argparse.ArgumentParser();p.add_argument('layout');p.add_argument('--depth',type=int,default=20);p.add_argument('--cap',type=int,default=100);p.add_argument('--seed',type=int,default=0);p.add_argument('--seconds',type=float,default=180);p.add_argument('--rule',default='clean');p.add_argument('--fixed',action='store_true');p.add_argument('--out',required=True);a=p.parse_args()
d=json.loads(Path(a.layout).read_text());sat6.B=ft.B=d['b'];sat6.C=ft.C=d['c'];hs=sorted(set(d['F'])-set(d['b'])-set(d['c'])-(set(d['a']) if d['args'].get('stageabc') else set()))
if a.fixed:os.environ['R0_FIXED_BASIS']='1'
if a.rule=='ideal':
 t0=time.monotonic();sol,sel,piv,edges,cells,af=sat6.build(a.depth,hs,a.seed,threads=1,maxcx=a.cap,pivfix=([d[k][i] for k in ['b','c'] for i in [0,1,3]] if a.fixed else None),rule='base');ok,model=sol.solve(time_limit=a.seconds)
 status='SAT' if ok else ('UNSAT' if ok is False else 'TIMEOUT');wall=time.monotonic()-t0;it=1;n=0;prep=None
 if ok:prep=dict(ops=[[list(e) for e in edges if model[se[e]]] for se in sel],pivots=[v for j in range(6) for v in cells if model[piv[j,v]]])
else:
 status,prep,wall,it,n=sat6.solve(a.depth,hs,a.seed,threads=1,pivfix=([d[k][i] for k in ['b','c'] for i in [0,1,3]] if a.fixed else None),K=a.cap,rule=a.rule,seconds=a.seconds)
r=dict(args=vars(a),B=d['b'],C=d['c'],helpers=hs,status=status,wall=wall,iters=it,fault_constraints=n)
if prep:
 r['cx']=sum(map(len,prep['ops']));Path(a.out+'.prep.json').write_text(json.dumps(prep,indent=2)+'\n')
Path(a.out+'.receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r),flush=True)
