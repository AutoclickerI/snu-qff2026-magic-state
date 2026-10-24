"""Assemble correlated resources using the existing native-time transplant."""
import os,sys,json,argparse
from pathlib import Path
sys.dont_write_bytecode=True
H=Path(__file__).resolve().parent;ROOT=H.parents[2]
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
sys.path[:0]=[str(ROOT/'work/lanes/BCPOL')]
import build as bc
os.environ['XTIM_TWIRL_CACHE_DIR']=str(H/'.xtim_cache')

def assemble(path,base='v23h_c2c9',window=0,init_mode='reset'):
 d=json.loads(Path(path).read_text());d['ops'].append([list(x) for x in zip(bc.B,bc.C)])
 d.update(kind='endpoint',value=0,endpoint_rank=3,extra_check=True,helper_x=False)
 options=dict(base=base,retime_window=window,endpoint_parity=True)
 if init_mode=='reset':options.update(mx=[],mz=[])
 elif init_mode=='fast':options['mx']=[q for q in d['pivots'] if q!=19]
 text,md=bc.build(d,options)
 stem=H/(Path(path).name.removesuffix('.prep.json')+f'_{base}_w{window}'+('' if init_mode=='reset' else '_'+('mi' if init_mode=='measured' else init_mode)))
 md.update(fresh_architecture='correlated rank-three BC with seven literal C checks',fresh_input=str(path))
 stem.with_suffix('.qasm').write_text(text);stem.with_suffix('.json').write_text(json.dumps(md,indent=2)+'\n')
 print(stem,md['CX'],md['native_depth'],flush=True);return stem

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('preps',nargs='+');p.add_argument('--base',default='v23h_c2c9');p.add_argument('--base-path');p.add_argument('--window',type=int,default=0);p.add_argument('--init-mode',default='reset');a=p.parse_args()
 if a.base_path:
  (H/'inputs').mkdir(exist_ok=True)
  for ext in ('.qasm','.json'):(H/'inputs'/(a.base+ext)).write_text(Path(a.base_path).with_suffix(ext).read_text())
  bc.H=H
 for s in a.preps:
  try:assemble(s,a.base,a.window,a.init_mode)
  except Exception as e:
   print(s,repr(e),flush=True)
   with (H/'REPORT.md').open('a') as f:f.write(f'\nAssembly `{Path(s).name}` failed: {e!r}. No physical score.\n')
