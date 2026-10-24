import os,sys,json,subprocess,time,concurrent.futures
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parents[3]
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
os.environ['PYTHONDONTWRITEBYTECODE']='1'
def run(name):
 row=dict(stem=name)
 for mode in ('speed','sparse'):
  with(H/(name+'.'+mode+'.log')).open('w')as f:p=subprocess.run([str(ROOT/'.venv/bin/python'),str(H/'evaluate.py'),mode,str(H/name)],stdout=f,stderr=subprocess.STDOUT)
  row[mode+'_exit']=p.returncode
  if p.returncode:break
  d=json.loads((H/(name+('.speed.json'if mode=='speed'else'.allorders.json'))).read_text());row[mode]=d.get('classification',d.get('loss'))
  if mode=='speed'and d['classification']=='SLOW':break
 print(json.dumps(row),flush=True);return row
with concurrent.futures.ThreadPoolExecutor(2)as ex:out=list(ex.map(run,json.loads((H/'encoder_sweep_stems.json').read_text())))
(H/'encoder_sweep.receipts.json').write_text(json.dumps(out,indent=2))
