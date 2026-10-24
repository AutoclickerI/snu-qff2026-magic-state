import os,sys,json,re,copy
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
ROOT=Path('/home/jihoon/competitions/quantumn');HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'work/lanes/SCHED'),str(ROOT/'work/lanes/EVAL'),str(ROOT/'work/lanes/TREP')]
import schedule as S
from util import native_times
_Unit=S.Unit
class NativeUnit(_Unit):
 def __init__(self,lines,raw_indices):
  if len(lines)==1 and lines[0].startswith('h '):
   self.lines=lines;self.raw_indices=raw_indices;self.name='H';self.qs=S.name_qs(lines[0])[1];self.last_is_measure=False
  else:super().__init__(lines,raw_indices)
S.Unit=NativeUnit
import xtim
xtim.cache_dir=str(HERE/'.xtim_cache')
A=[1,14,8,9,2,16,15];B=[6,26,13,11,4,23,27];C=[12,25,19,17,5,29,28];D=[0,20,7,10,3,22,21]

def base():
 text=(HERE/'base.qasm').read_text();meta=json.loads((HERE/'base.json').read_text())
 h,r,tail=S.qasm_ops(text);units=S.fold_units(r);times=native_times(text,units)
 init={q:max(i for i,u in enumerate(units) if times[i]<45 and u.qs==(q,) and u.name in ('RESET','RX')) for q in A}
 ai={i for i,u in enumerate(units) if times[i]<45 and set(u.qs)<=set(A) and all(i>=init[q] for q in u.qs)}
 assert len(ai)==18
 return h,units,tail,times,meta,init,ai

def emit(name,units,times,tail,meta=None):
 h=['OPENQASM 2.0;','include "qelib1.inc";','qreg q[36];','creg c[256];']
 text=S.emit(h,units,times,tail)
 hh,rr,tt=S.qasm_ops(text);nu=S.fold_units(rr);nt=native_times(text,nu)
 wanted=[(t,u.lines) for t,u in sorted(zip(times,units),key=lambda x:x[0])]
 assert [(t,u.lines) for t,u in zip(nt,nu)]==wanted,('native mismatch',name)
 p=HERE/name;p.with_suffix('.qasm').write_text(text)
 md=dict(data_qubits=D,cx=sum(u.name=='CX' for u in nu),native_depth=max(nt)+1);md.update(meta or {})
 p.with_suffix('.json').write_text(json.dumps(md,indent=1))
 return p

def unit(lines):return S.Unit(lines,[])
