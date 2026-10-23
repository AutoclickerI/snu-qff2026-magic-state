import os,sys,json,time,math
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
HERE=Path(__file__).resolve().parent;os.chdir(HERE);sys.path.insert(0,str(HERE.parent/'EVAL'))
from exact2 import Eval,run
import xtim
xtim.cache_dir=str(HERE/'.xtim_cache')
st=sys.argv[1];d=json.loads(Path(st+'.json').read_text());t=time.time();e=Eval(Path(st+'.qasm').read_text(),d['data_qubits']);r=run(e,1)
out=dict(first=r['loss1'],second=r['loss'],exp_A1=math.exp(-r['A1']),seconds=time.time()-t)
Path(st+'_second.json').write_text(json.dumps(out,indent=2)+'\n');print(st,out,flush=True)
