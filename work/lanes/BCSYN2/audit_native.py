import os,sys,json
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'work/lanes/SCHED'),str(ROOT/'work/lanes/TREP2')]
import schedule as S
from util import native_times
text=(HERE/'inputs/v20.qasm').read_text();h,r,s=S.qasm_ops(text);u=S.fold_units(r);ts=native_times(text,u)
rows=[dict(index=i,time=t,lines=x.lines,name=x.name,qubits=x.qs) for i,(x,t) in enumerate(zip(u,ts))]
(HERE/'v20_native.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows))
