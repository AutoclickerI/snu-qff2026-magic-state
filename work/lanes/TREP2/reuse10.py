"""Combine EARLYBC's verified measured-|+> transfer with TREP encoders."""
import os,sys,json
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path[:0]=[str(OUT),str(OUT/'inputs'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
from schedules import write
from exact2 import Eval

if __name__=='__main__':
    for name in sys.argv[1:]:
        stem=OUT/name;text=stem.with_suffix('.qasm').read_text();meta=json.loads(stem.with_suffix('.json').read_text());h,r,t=S.qasm_ops(text);u=S.fold_units(r);ts=native_times(text,u)
        mx=next(i for i,z in enumerate(u)if z.lines==['h q[10];','measure q[10] -> c[8];'])
        seq=[i for i in range(mx+1,len(u))if 10 in u[i].qs]
        reset,first,second=seq[:3]
        assert u[reset].lines==['reset q[10];']
        assert u[first].lines==['cx q[4],q[10];'] and u[second].lines==['cx q[10],q[4];']
        u[mx]=S.Unit(['h q[10];','measure q[10] -> c[8];','h q[10];'],[])
        u[first]=S.Unit(['cx q[10],q[4];'],[]);u[second]=S.Unit(['cx q[4],q[10];'],[])
        nu=[z for i,z in enumerate(u)if i!=reset];nt=[v for i,v in enumerate(ts)if i!=reset]
        # Emit the compact base before applying the same rigid-suffix ALAP solve.
        txt=S.emit(h,nu,nt,t);s=OUT/(name+'_reuse10');s.with_suffix('.qasm').write_text(txt)
        hh,rr,tt=S.qasm_ops(txt);uu=S.fold_units(rr);ns=native_times(txt,uu)
        meta.update(source=name,pre_end=max(v for z,v in zip(uu,ns)if z.name in('T','TDG')),reuse_source='work/lanes/EARLYBC/reuse.py: measured |+> q10, reverse two-CX transfer, remove reset')
        s.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
        ev=Eval(txt,meta['data_qubits']);print(s.name,'c1',float(ev.fp@ev.n_single),flush=True)
