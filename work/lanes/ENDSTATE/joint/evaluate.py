import os,sys,json,time,argparse,importlib.util,runpy
from pathlib import Path
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
H=Path(__file__).resolve().parent;ROOT=H.parents[3];sys.path[:0]=[str(ROOT/'work/lanes/EVAL'),str(ROOT/'work')]
import xtim
xtim.cache_dir=str(H/'.xtim_cache');os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
p=argparse.ArgumentParser();p.add_argument('mode',choices=['exact','check','sparse','speed','mc3','singles']);p.add_argument('stem');p.add_argument('--procs',type=int,default=4);a=p.parse_args();stem=Path(a.stem).resolve();start=time.monotonic()
if a.mode=='exact':
 sys.argv=[str(ROOT/'work/lanes/EVAL/exact2.py'),str(stem.with_suffix('.qasm')),'--procs',str(a.procs),'--third','--json',str(stem.with_suffix('.sens.json'))];runpy.run_path(sys.argv[0],run_name='__main__')
elif a.mode in('check','singles'):
 if a.mode=='singles':
  import exact2,math
  e=exact2.Eval(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits']);out=dict(c1=float(e.fp@e.n_single),acceptance_proxy=math.exp(-float(e.fp@(1-e.a_single))),detectors=len(e.e.projs),rank=e.e.r)
 else:
  import fast_check
  r=fast_check.check(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits'],shots=10**6,seed=0,procs=a.procs);out=dict(passed=r.passed,score=r.score,sem=r.sem,acceptance=r.acceptance,n_2q=r.n_2q,details=str(r),seconds=time.monotonic()-start)
 stem.with_suffix('.'+a.mode+'.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
elif a.mode=='sparse':
 sys.path.insert(0,str(H/'sparse_snapshot'));import sparse_walsh as sw
 sw.__file__=str(H/'sparse_walsh_output.py');out=sw.run(stem,72,True);stem.with_suffix('.allorders.json').write_text(json.dumps(out,indent=2))
elif a.mode=='speed':
 spec=importlib.util.spec_from_file_location('unchanged_speed',H/'tool_snapshot/speed_predict.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.xtim.cache_dir=str(H/'.xtim_cache');out=mod.predict(str(stem));stem.with_suffix('.speed.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
else:
 sys.argv=[str(H/'tool_snapshot/mc3.py'),str(stem),'--procs',str(a.procs)];runpy.run_path(sys.argv[0],run_name='__main__')
(H/(stem.name+'.'+a.mode+'.exit.json')).write_text(json.dumps(dict(exit_code=0,seconds=time.monotonic()-start),indent=2))
