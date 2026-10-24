"""Unchanged XTIM predictor function, with its cache relocated to this lane."""
import os,sys,importlib.util,json
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
for k in('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
spec=importlib.util.spec_from_file_location('xtim_speed_predict',ROOT/'work/lanes/XTIM/speed_predict.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);mod.xtim.cache_dir=str(H/'.xtim_cache')
r=mod.predict(sys.argv[1]);Path(sys.argv[1]).with_suffix('.speed_prediction.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
