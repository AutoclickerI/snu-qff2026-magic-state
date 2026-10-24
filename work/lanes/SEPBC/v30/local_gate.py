from pathlib import Path
import os,sys,subprocess,json,time
V=Path(__file__).resolve().parent;H=V.parent;ROOT=H.parents[2];PY=ROOT/'.venv/bin/python'
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',XTIM_TWIRL_CACHE_DIR=str(H/'.xtim_cache'))
for name in sys.argv[1:]:
 st=V/name;r={}
 for label,args in [('judge',[ROOT/'work/fast_check.py',st.with_suffix('.qasm'),st.with_suffix('.json'),'1000000','1']),('speed',[H/'speed_local.py',st])]:
  t=time.monotonic()
  with st.with_suffix('.'+label+'.log').open('w')as f:p=subprocess.run([str(PY),*map(str,args)],cwd=ROOT,env=os.environ,stdout=f,stderr=subprocess.STDOUT)
  r[label]=dict(returncode=p.returncode,wall_seconds=time.monotonic()-t)
  assert not p.returncode,r
 st.with_suffix('.local_gate.json').write_text(json.dumps(r,indent=2));print(name,r,flush=True)
