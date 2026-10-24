import os,sys,json,re
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.dont_write_bytecode=True
import tprep.qasm as tq,tprep.noise as tn
from route import P0
H=Path(__file__).resolve().parent
stem=Path(sys.argv[1]);d=json.loads(Path(str(stem)+'.json').read_text());lay=json.loads(Path(d['source']['layout']).read_text());k,tr,tc=map(int,lay['args']['transform'].split(','))
def tf(q):
 r,c=divmod(q,6);return [(r,c),(r,5-c),(5-r,c),(5-r,5-c),(c,r),(c,5-r),(5-c,r),(5-c,5-r)][k]
r0=min(tf(q)[0] for q in P0);c0=min(tf(q)[1] for q in P0)
def mp(q):r,c=tf(q);return (r-r0+tr)*6+c-c0+tc
P=set(map(mp,P0))
def atoms(txt,baseline=False):
 st,_,err=tq.convert(txt);assert not err,err
 prog,steps,gaps=tn.schedule(st);out=[]
 for ins,sts in zip(prog,steps):
  for qs,t in sts:
   if t>32:continue
   if baseline or set(qs)<=P:
    if qs:out.append((t,ins.name,tuple(mp(q) for q in qs) if baseline else tuple(qs)))
 return sorted(out)
a=atoms((H/'v16_bc2m.qasm').read_text(),True);b=atoms(Path(str(stem)+'.qasm').read_text());assert a==b,(set(a)-set(b),set(b)-set(a))
out=dict(status='PASS',prefix_native_operations=len(a),steps='0..32',transform=lay['args']['transform']);Path(str(stem)+'.prefix.json').write_text(json.dumps(out,indent=2)+'\n');print(out)
