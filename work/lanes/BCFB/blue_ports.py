import os,sys
sys.dont_write_bytecode=True
for k in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,time,traceback
from build import build,H,source
from evaluate import score
D=H/'blue'
def save(tag,text,md):
 start=time.monotonic();row=score(text,md);row.update(tag=tag,context=md.get('options',{}).get('context',tag),options=md.get('options',{}),CX=md.get('CX',md.get('cx')),seconds_all=time.monotonic()-start)
 p=D/'finalists'/tag;p.with_suffix('.qasm').write_text(text);p.with_suffix('.json').write_text(json.dumps(md,indent=2));p.with_suffix('.screen.json').write_text(json.dumps(row,indent=2));print(json.dumps(row),flush=True);return row
baseprep=json.loads((H/'inputs/fb_s401_0035.prep.json').read_text())
for context in ['v25k','v26n']:
 p=D/'inputs'/context;md=json.loads(p.with_suffix('.json').read_text());orig=save(context,p.with_suffix('.qasm').read_text(),md)
 for variant in ['project','alap']:
  opt=dict(context=context,timing=variant,mx=[q for q in baseprep['pivots'] if q!=19]);text,md=build(baseprep,opt);row=save(context+'_replay_'+variant,text,md)
  if variant=='project':assert abs(row['total']-orig['total'])<1e-15,(orig,row)
 for f in sorted((H/'finalists').glob('*.json')):
  if f.name.endswith(('.screen.json','.exact.json','.diff.json')):continue
  d=json.loads(f.read_text());prep=d.get('prep')
  if not prep:continue
  for mode in ['preserve','late','reset']:
   opt=dict(d.get('options',{}),context=context,mx=[q for q in prep['pivots'] if q!=19] if mode!='reset' else [],late_mx=mode=='late',init_checks=d.get('init_checks',[]))
   tag=context+'_'+f.stem+'_'+mode
   try:text,md=build(prep,opt);save(tag,text,md)
   except (AssertionError,ValueError) as e:print(json.dumps(dict(tag=tag,error=str(e))),flush=True)
