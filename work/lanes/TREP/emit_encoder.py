"""Emit a solver witness, eliminating empty layers and never-used preparations."""
import os,sys,json,re,argparse
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'work/lanes/SCHED'),str(ROOT/'work/lanes/EVAL')]
import schedule as S
from util import native_times
from exact2 import Eval

def build(witness,name):
    row=json.loads((OUT/witness).read_text());network=[L for L in row['network']if L];D=len(network);zs=row['zero'];tq=row['T_site']
    cells=sorted(set([tq]+zs+[q for L in network for e in L for q in e]))
    src=(OUT/'inputs/v17a.qasm').read_text();head,raw,tail=S.qasm_ops(src);units=S.fold_units(raw);times=native_times(src,units)
    old={i for i,u in enumerate(units)if times[i]<=10 or (times[i]==11 and u.name=='CX') or (times[i]==12 and u.lines==['cx q[10],q[4];'])}
    shift=D-9;newunits=[];newtimes=[]
    for i,u in enumerate(units):
        if i not in old:newunits.append(u);newtimes.append(times[i]+shift)
    for q in cells:
        lines=[f'measure q[{q}] -> c[{39+zs.index(q)}];']if q in zs else [f'reset q[{q}];',f'h q[{q}];']
        first=min([l+2 for l,L in enumerate(network)if any(q in e for e in L)]or[D+2])
        newunits.append(S.Unit(lines,[]));newtimes.append(0 if q==tq else first-1)
    newunits.append(S.Unit([f't q[{tq}];'],[]));newtimes.append(1)
    for l,L in enumerate(network):
        for c,t in L:newunits.append(S.Unit([f'cx q[{c}],q[{t}];'],[]));newtimes.append(l+2)
    text=S.emit(head,newunits,newtimes,tail);d=[0,20,7,10,3,22,21]
    h,r,t=S.qasm_ops(text);u=S.fold_units(r);ts=native_times(text,u)
    R=max(t for a,t in zip(u,ts)if a.lines==['cx q[0],q[1];'])
    pre_end=max(t for a,t in zip(u,ts)if a.name in ('T','TDG'))
    meta=dict(data_qubits=d,R=R,pre_end=pre_end,form='f00_0',injection_cx=sum(map(len,network)),injection_cx_layers=D,source_witness=witness)
    stem=OUT/name;stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    ev=Eval(text,d);print(name,meta,'c1',float((ev.fp*ev.n_single).sum()),flush=True)

if __name__=='__main__':build(sys.argv[1],sys.argv[2])
