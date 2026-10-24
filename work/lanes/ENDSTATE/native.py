import sys,os,re,json,collections
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.path[:0]=[str(ROOT/'work/lanes/SCHED'),str(ROOT/'work/lanes/TREP'),str(ROOT/'work/lanes/EVAL'),str(ROOT/'work')]
import schedule as S
from util import native_times
import xtim
xtim.cache_dir=str(H/'.xtim_cache')
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
class Unit(S.Unit):
 def __init__(self,lines,raw_indices=()):
  if len(lines)==1 and lines[0].startswith('h '):
   self.lines=lines;self.raw_indices=list(raw_indices);self.name='H';self.qs=S.name_qs(lines[0])[1];self.last_is_measure=False
  else:super().__init__(lines,list(raw_indices))
S.Unit=Unit
PD=[0,20,7,4,3,15,8]
def read(stem):
 text=Path(str(stem)+'.qasm').read_text();head,raw,tail=S.qasm_ops(text);us=S.fold_units(raw);ts=native_times(text,us)
 return head,[dict(lines=u.lines,t=t,id=i,name=u.name,qs=list(u.qs))for i,(u,t)in enumerate(zip(us,ts))],tail
if __name__=='__main__':
 for name in ['v23h_c2c9','v29c']:
  h,ops,tail=read(ROOT/'work/lanes/MAIN'/name)
  (H/(name+'.native.json')).write_text(json.dumps(dict(head=h,ops=ops,tail=tail),indent=2))
  print(name)
  for o in ops:
   if o['t']>=20 and (o['name']=='TDG' or (set(o['qs'])&{4,9,10,15,16} and o['t']<=42)):print(o)
  print('detectors',tail)
