import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from build import build,H
from evaluate import score
import json
D=H/'blue'
for context in ['v25k','v26n']:
 for f in sorted((H/'finalists').glob('*.json')):
  if f.name.endswith(('.screen.json','.exact.json','.diff.json')):continue
  d=json.loads(f.read_text());prep=d.get('prep')
  if not prep:continue
  opt=dict(d.get('options',{}),context=context,mx=[q for q in prep['pivots'] if q!=19],auto_fast=True,init_checks=d.get('init_checks',[]),retime_window=2)
  tag=context+'_'+f.stem+'_auto'
  try:
   text,md=build(prep,opt);row=score(text,md);row.update(tag=tag,context=context,options=md['options'],CX=md['CX']);p=D/'finalists'/tag;p.with_suffix('.qasm').write_text(text);p.with_suffix('.json').write_text(json.dumps(md,indent=2));p.with_suffix('.screen.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True)
  except (AssertionError,ValueError) as e:print(json.dumps(dict(tag=tag,error=str(e))),flush=True)
