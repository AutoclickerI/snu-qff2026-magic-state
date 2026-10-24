"""Validate pending fully gated candidates on the owning host."""
import sys,json,datetime,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import pop36_support as v,pop36_finalize as f
host=sys.argv[1];jobs=[]
for p in v.OUT.glob('*/*.gate.json'):
 g=json.loads(p.read_text());remote=p.parent.name=='owl' or p.parent.name=='seed1'
 if remote!=(host=='owl')or not g.get('gated')or isinstance(g.get('MC3'),dict):continue
 jobs.append((g['loss'],p))
for _,p in sorted(jobs):
 g=json.loads(p.read_text());st=Path(g['stem']);expanded=datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime(2026,10,24,17,20,tzinfo=datetime.timezone.utc);procs=15 if expanded else 7
 print('MC3_START',str(st),procs,flush=True);f.mc(st,procs)
print('MC3_ALL_DONE',host,len(jobs),flush=True)
