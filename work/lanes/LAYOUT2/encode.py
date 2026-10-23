import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json, argparse
from pathlib import Path
import exenc
ap=argparse.ArgumentParser();ap.add_argument('layout');ap.add_argument('--workers',type=int,default=2);ap.add_argument('--extra',type=int,default=1);a=ap.parse_args()
path=Path(a.layout).resolve();l=json.loads(path.read_text());out=path.with_name(path.stem+'_A.json')
r=exenc.run(l['a'],'plus',[],a.extra,out,a.workers,False,True)
ps=r.get('pareto',[])
good=[c for c in ps if all(c['danger_vector_units'][j+1]==0 for j in l['M'])]
good.sort(key=lambda c:(c['depth'],c['cx'],c['danger_units']))
out.with_name(out.stem+'_filtered.json').write_text(json.dumps(good,indent=2)+'\n')
print('FILTER',path.stem,'M',l['M'],'pareto',len(ps),'caught',len(good),flush=True)
for c in good[:10]:print(c['depth'],c['cx'],c['danger_vector_units'],flush=True)
