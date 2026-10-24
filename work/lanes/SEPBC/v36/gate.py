from pathlib import Path
import os,sys,json,subprocess,time
V=Path(__file__).resolve().parent;H=V.parent;ROOT=H.parents[2];PY=ROOT/'.venv/bin/python';os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',XTIM_TWIRL_CACHE_DIR=str(H/'.xtim_cache'))
for name in sys.argv[1:]:
 st=V/name;rec={}
 for label,args in [('judge',[ROOT/'work/fast_check.py',st.with_suffix('.qasm'),st.with_suffix('.json'),'1000000','1']),('speed',[H/'speed_local.py',st])]:
  t=time.monotonic()
  with st.with_suffix('.'+label+'.log').open('w')as f:r=subprocess.run([str(PY),*map(str,args)],cwd=ROOT,env=os.environ,stdout=f,stderr=subprocess.STDOUT)
  assert r.returncode==0;(rec.update({label:dict(returncode=0,seconds=time.monotonic()-t)}))
 st.with_suffix('.gate.json').write_text(json.dumps(rec,indent=2));print(name,rec,flush=True)
