import os,sys,json,time,importlib.util
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')
sys.path.insert(0,str(ROOT/'work'))
import xtim,fast_check
xtim.cache_dir=str(H/'.xtim_cache')
spec=importlib.util.spec_from_file_location('speed_predict',H/'speed_predict.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
xtim.cache_dir=str(H/'.xtim_cache')
for name in sys.argv[1:]:
    p=H/name;start=time.monotonic();r={}
    try:
        r['speed']=mod.predict(str(p))
        if r['speed']['classification']=='FAST':
            t=time.monotonic()
            report=fast_check.check(p.with_suffix('.qasm').read_text(),json.loads(p.with_suffix('.json').read_text())['data_qubits'],shots=10**6,seed=0,procs=1)
            r.update(passed=report.passed,acceptance=report.acceptance,score=report.score,judge_seconds=time.monotonic()-t,report=str(report))
    except Exception as e:r['error']=repr(e)
    r['seconds']=time.monotonic()-start
    p.with_suffix('.gate.json').write_text(json.dumps(r,indent=2)+'\n');print(name,json.dumps(r),flush=True)
