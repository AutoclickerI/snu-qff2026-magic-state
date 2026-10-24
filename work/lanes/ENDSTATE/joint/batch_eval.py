import os,sys,json,subprocess,time,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
stems=json.loads(Path(sys.argv[1]).read_text());modes=sys.argv[2].split(',');workers=int(sys.argv[3]);procs=int(sys.argv[4])
def run(name):
 results=[]
 for mode in modes:
  out=H/(name+'.'+mode+'.log');start=time.monotonic()
  with out.open('w')as f:r=subprocess.run([str(ROOT/'.venv/bin/python'),str(H/'evaluate.py'),mode,str(H/name),'--procs',str(procs)],stdout=f,stderr=subprocess.STDOUT,cwd=ROOT)
  rec=dict(stem=name,mode=mode,exit_code=r.returncode,seconds=time.monotonic()-start);results.append(rec);print(json.dumps(rec),flush=True)
  if r.returncode:break
 return results
with concurrent.futures.ThreadPoolExecutor(workers)as ex:out=list(ex.map(run,stems))
(H/('batch_'+Path(sys.argv[1]).stem+'.'+sys.argv[2].replace(',','_')+'.receipts.json')).write_text(json.dumps(out,indent=2))
