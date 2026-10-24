from pathlib import Path
import os,sys,json,subprocess,argparse
V=Path(__file__).resolve().parent;H=V.parent;ROOT=H.parents[2];os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',XTIM_TWIRL_CACHE_DIR=str(H/'.xtim_cache'))
p=argparse.ArgumentParser();p.add_argument('stems',nargs='+');p.add_argument('--procs',type=int,default=8);a=p.parse_args()
for name in a.stems:
 st=V/name
 with st.with_suffix('.allorders.log').open('w')as f:r=subprocess.run([str(ROOT/'.venv/bin/python'),'-u',str(V/'sparse/sparse_walsh.py'),str(st),'72','canonical',str(a.procs)],cwd=ROOT,env=os.environ,stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode==0,(name,r.returncode)
 row=json.loads((V/'sparse'/(name+'_canonical_sparse_result.json')).read_text());st.with_suffix('.allorders.json').write_text(json.dumps(row,indent=2));print(name,row['loss'],row['acceptance'],flush=True)
 with(H/'REPORT.md').open('a')as f:f.write(f'\nAll orders `{name}`: {row["loss"]:.12e}, acceptance{row["acceptance"]:.9f}. Judge/speed/MC are separate gates.\n')
