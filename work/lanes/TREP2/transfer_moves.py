"""Transfer the two measured timing improvements across injection encoders."""
import os,sys,json
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path[:0]=[str(OUT),str(OUT/'inputs'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
from schedules import write

if __name__=='__main__':
    for name in sys.argv[1:]:
        stem=OUT/name;meta=json.loads(stem.with_suffix('.json').read_text());text=stem.with_suffix('.qasm').read_text();h,r,t=S.qasm_ops(text);u=S.fold_units(r);ts=native_times(text,u);pre=set(meta['prefix_unit_indices']);changes=[]
        i=max((i for i,v in enumerate(u)if i in pre and v.lines==['cx q[8],q[14];']),key=lambda i:ts[i]);j=next(i for i,v in enumerate(u)if v.lines==['cx q[12],q[6];'])
        for k in(i,j):changes.append(dict(operation=u[k].lines,old=ts[k],new=ts[k]-1));ts[k]-=1
        pred,succ=S.build_dag(u);assert S.feasible(ts,u,pred,succ)
        write(name,name+'_two_moves',ts,u,h,t,dict(meta,transferred_moves=changes))
