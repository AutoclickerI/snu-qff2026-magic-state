import os,sys,json,importlib.util,time
from pathlib import Path
H=Path(__file__).resolve().parent
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
spec=importlib.util.spec_from_file_location('speed',H/'tool_snapshot/speed_predict.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.xtim.cache_dir=str(H/'.xtim_cache')
for name in json.loads((H/'partial_reuse_stems.json').read_text()):
 r=mod.predict(str(H/name),shots=5000,repeats=1);(H/(name+'.speed_screen.json')).write_text(json.dumps(r,indent=2));print(name,r['classification'],r['median_seconds_per_1e6'],flush=True)
