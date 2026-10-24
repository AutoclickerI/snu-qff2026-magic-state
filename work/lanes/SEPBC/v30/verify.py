"""Required unchanged exact2, sparse all orders, ablation and conditional MC."""
import os,sys,json,subprocess,argparse,concurrent.futures,hashlib
from pathlib import Path
V=Path(__file__).resolve().parent;H=V.parent;ROOT=H.parents[2];PY=ROOT/'.venv/bin/python'
os.environ.update(OMP_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1',XTIM_TWIRL_CACHE_DIR=str(H/'.xtim_cache'))
def cmd(args,out):
 with out.open('w')as f:p=subprocess.run([str(PY),'-u',*map(str,args)],cwd=ROOT,env=os.environ,stdout=f,stderr=subprocess.STDOUT)
 if p.returncode:raise RuntimeError((args,p.returncode,str(out)))
def run(name):
 st=V/name;receipt={};rpath=st.with_suffix('.verify.json')
 from canonical_detectors import canonical
 exact_stem,guard=canonical(st);receipt['detector_guard']=guard
 for label,args,ext in [
 ('exact',[ROOT/'work/lanes/EVAL/exact2.py',exact_stem.with_suffix('.qasm'),'--third','--top','30','--procs',os.environ.get('SEPBC_EXACT_PROCS','2'),'--json',st.with_suffix('.exact.json')],'.exact.log'),
 ('allorders',[V/'sparse/sparse_walsh.py',st,'72','canonical'],'.allorders.log'),
 ('ablation',[V/'ablate.py',st,'--procs','1'],'.ablation.log')]:
  cmd(args,st.with_suffix(ext));receipt[label]='complete';rpath.write_text(json.dumps(receipt,indent=2));print(name,label,flush=True)
 sparse=V/'sparse'/(name+'_canonical_sparse_result.json');ao=json.loads(sparse.read_text());st.with_suffix('.allorders.json').write_text(json.dumps(ao,indent=2))
 if ao['loss']<5.8937742042181006e-5:
  cmd([H/'inputs/mc3.py',st,'--procs',os.environ.get('SEPBC_MC_PROCS','4')],st.with_suffix('.mc.log'));receipt['mc']='complete';rpath.write_text(json.dumps(receipt,indent=2));print(name,'MC complete',flush=True)
 with(H/'REPORT.md').open('a')as f:f.write(f'\nVerified `{name}`: all orders {ao["loss"]:.12e}, acceptance {ao["acceptance"]:.9f}; unchanged exact2 and ablations complete; MC={receipt.get("mc","not triggered")}.\n')
 return receipt
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('names',nargs='+');p.add_argument('--jobs',type=int,default=3);a=p.parse_args()
 with concurrent.futures.ThreadPoolExecutor(a.jobs)as pool:list(pool.map(run,a.names))
