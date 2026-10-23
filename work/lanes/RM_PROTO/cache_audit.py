import os,sys,json,time
sys.dont_write_bytecode=True
from score import *
import xtim.reference as ref
keys=set();original=ref.resolve_reference

def traced(text,source='xtim-circuit'):
 keys.add(ref.cache_key(text));return original(text,source)
ref.resolve_reference=traced
for name in ['rm_circuit','va_ta0_PA','va_ta02_PA','va_TA_PA']:
 q=(BASE/(name+'.qasm')).read_text();j=json.loads((BASE/(name+'.json')).read_text());s,_,err=tq.convert(q)
 r=tc.check_stim(s,j['data_qubits'],shots=64,p=0,seed=0);assert r.correct_ok
# Capture region key in worker process by switching the worker to in-process for 64 diagnostic shots.
import regions
class InlinePool:
 def __enter__(self):return self
 def __exit__(self,*a):pass
 def map(self,fn,args):return list(map(fn,args))
class Context:
 def Pool(self,*a,**k):return InlinePool()
regions.mp.get_context=lambda *a:Context()
sys.argv=['regions.py',str(BASE/'va_ta0_PA'),'64','1'];regions.main3()
removed=[]
for key in keys:
 for suffix in ['.ref','.ref.sha256','.ref.defsig']:
  p=ROOT/'.xtim_cache'/(key+suffix)
  if p.exists():
   # Only lane-specific exact circuit keys, not a blanket directory cleanup.
   removed.append({'path':str(p),'mtime':p.stat().st_mtime,'bytes':p.stat().st_size});p.unlink()
(BASE/'cache_audit.json').write_text(json.dumps({'cache_directory':str(xtim.cache_dir),'keys':sorted(keys),'removed_accidental_root_entries':removed},indent=2)+'\n')
print('moved reference caching into lane; removed',len(removed),'lane-specific root cache files',flush=True)
