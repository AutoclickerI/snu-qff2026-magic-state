import os,sys,json
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import tprep.qasm as tq,tprep.noise as tn
from packing import P
H=Path(__file__).resolve().parent

def atoms(txt,baseline=False):
 st,_,err=tq.convert(txt);assert not err,err
 prog,steps,gaps=tn.schedule(st);out=[]
 for ins,sts in zip(prog,steps):
  for qs,t in sts:
   if qs and t<=32 and (baseline or set(qs)<=P):out.append((t,ins.name,tuple(qs)))
 return sorted(out)
a=atoms((H.parents[1]/'candidates/v16_bc2m.qasm').read_text(),True)
for name in sys.argv[1:]:
 stem=H/name;b=atoms(stem.with_suffix('.qasm').read_text());assert a==b,(name,set(a)-set(b),set(b)-set(a))
 out=dict(status='PASS',prefix_native_operations=len(a),steps='0..32',transform='identity');Path(str(stem)+'.prefix.json').write_text(json.dumps(out,indent=2)+'\n');print(name,out)
