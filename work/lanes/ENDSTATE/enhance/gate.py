from common import *
import argparse,importlib.util,runpy
p=argparse.ArgumentParser();p.add_argument('mode',choices=['speed','check','mc3']);p.add_argument('stem');p.add_argument('--procs',type=int,default=8);a=p.parse_args();stem=Path(a.stem).resolve();start=time.monotonic()
if a.mode=='speed':
 spec=importlib.util.spec_from_file_location('speed',H/'tool_snapshot/speed_predict.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.xtim.cache_dir=str(H/'.xtim_cache');r=m.predict(str(stem));stem.with_suffix('.speed.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
elif a.mode=='check':
 import fast_check
 r=fast_check.check(stem.with_suffix('.qasm').read_text(),json.loads(stem.with_suffix('.json').read_text())['data_qubits'],shots=10**6,seed=0,procs=a.procs);out=dict(passed=r.passed,score=r.score,sem=r.sem,acceptance=r.acceptance,details=str(r),seconds=time.monotonic()-start);stem.with_suffix('.check.json').write_text(json.dumps(out,indent=2));print(json.dumps(out),flush=True)
else:
 sys.argv=[str(H/'tool_snapshot/mc3.py'),str(stem),'--procs',str(a.procs)];runpy.run_path(sys.argv[0],run_name='__main__')
(H/(stem.name+'.'+a.mode+'.exit.json')).write_text(json.dumps(dict(exit_code=0,seconds=time.monotonic()-start)))
