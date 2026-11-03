import os,sys,json,itertools,copy,concurrent.futures
from pathlib import Path
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
R=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
sys.path[:0]=[str(R/'work/lanes/NATIVE2_20261027'),str(R/'work/lanes/REBUILD20261027'),str(R/'work/tools')]
from incumbent_a_sx import f,emit
from qtools.validity import raw_check
P=next((R/'work/lanes/SOTA_20261028/native_best').glob('*.qasm'));orig,dets=f.parse_current(P.read_text());D=[6,20,19,10,2,22,16]
targets=[(41,(9,15)),(42,(21,15)),(43,(15,14)),(44,(15,9)),(45,(9,15))]
def run(row):
 choices,keepfinal=row;ops=[]
 for o in orig:
  if o.bit==322 or (o.kind=='CX' and (o.time,o.qs)==(39,(16,15))):continue
  if o.kind=='CX' and (o.time,o.qs)==(46,(16,15)) and not keepfinal:continue
  match=next((i for i,p in enumerate(targets) if (o.time,o.qs)==p and o.kind=='CX'),None)
  if match is not None:
   choice=choices[match]
   if choice==0:continue
   if choice==2:o=copy.deepcopy(o);o.qs=o.qs[::-1]
  ops.append(o)
 text=emit(ops,[]);raw=raw_check(text,D)
 return dict(choices=list(choices),keepfinal=keepfinal,raw=raw)
if __name__=='__main__':
 jobs=list(itertools.product(itertools.product(range(3),repeat=5),range(2)));out=[]
 with concurrent.futures.ProcessPoolExecutor(max_workers=2) as pool:
  for i,res in enumerate(pool.map(run,jobs,chunksize=4)):
   out.append(res)
   if res['raw']['ok']:print('FOUND',json.dumps(res),flush=True)
   if i%50==0:print('completed',i,flush=True)
 (H/'isometry_search.json').write_text(json.dumps(out,indent=2)+'\n')
