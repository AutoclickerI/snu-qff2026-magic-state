"""Exact moment screen with arbitrary-width detector masks; no judge edits.
Only the detector-array integer representation is replaced. Every requested
vectorized table is checked against the existing scalar table implementation.
"""
import os,sys,json,inspect,hashlib,time,importlib.util
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[2];sys.path[:0]=[str(ROOT/'work/lanes/EVAL'),str(ROOT/'work')]
import exact2,engine,numpy as np,xtim
xtim.cache_dir=str(H/'.xtim_cache');os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
source=inspect.getsource(engine.batch_tables);replacement=source.replace('D = np.asarray(D, dtype=np.int64)','D = np.asarray(D, dtype=object)');assert replacement!=source
ns=vars(engine).copy();exec(compile(replacement,'ENDSTATE:wide_batch_tables','exec'),ns);wide=ns['batch_tables'];checked=0

def checked_tables(self,S,D):
 global checked
 aa,ee=wide(self,S,D)
 for j,(s,d)in enumerate(zip(S,D)):
  ref=self.table(int(s),int(d))
  if ref is None:assert abs(aa[j])<1e-14 and np.max(np.abs(ee[j]))<1e-14
  else:assert abs(aa[j]-ref[0])<1e-13 and np.max(np.abs(ee[j]-ref[1]))<1e-13
  checked+=1
 return aa,ee
engine.Engine.batch_tables=checked_tables
spec=importlib.util.spec_from_file_location('sepbc_exact_moments',ROOT/'work/lanes/SEPBC/moments.py');mom=importlib.util.module_from_spec(spec);spec.loader.exec_module(mom)
for arg in sys.argv[1:]:
 stem=Path(arg);start=time.monotonic();ev=exact2.Eval(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits']);prior=checked;r=mom.evaluate(ev);r.update(detector_projectors=len(ev.e.projs),verified_scalar_tables=checked-prior,seconds_total=time.monotonic()-start,scope='unchanged SEPBC moment arithmetic; only vectorized detector-mask dtype changed from int64 to Python integer; every requested table checked against unchanged EVAL scalar table',engine_source_sha256=hashlib.sha256(source.encode()).hexdigest())
 stem.with_suffix('.wide_screen.json').write_text(json.dumps(r,indent=2));print(stem,json.dumps(r),flush=True)
