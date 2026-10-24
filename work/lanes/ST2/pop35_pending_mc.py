"""Finish every announced finalist, split by artifact scope across hosts."""
import sys,json,datetime,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import pop35_support as v
import v35_finalize as f
v.a.BASE_LOSS=4.376021340833061e-5;v.a.BASE_ACC=.5016883498058476
host=sys.argv[1]
if host=='zebra':(v.OUT/'migrate_zebra_at_checkpoint').unlink(missing_ok=True)
jobs=[]
for p in v.OUT.glob('*/*.gate.json'):
 r=json.loads(p.read_text());rel=p.relative_to(v.OUT);remote=rel.parts[0]=='owl' or (rel.parts[0]=='zebra'and rel.name.startswith(('g00_','g01_','g02_','g03_')))
 if remote!=(host=='owl')or not r.get('gated')or isinstance(r.get('MC3'),dict):continue
 jobs.append((r['loss'],p))
for _,p in sorted(jobs):
 r=json.loads(p.read_text());st=Path(r['stem']);expanded=datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime(2026,10,24,16,20,tzinfo=datetime.timezone.utc);procs=int(sys.argv[2]) if len(sys.argv)>2 else ((23 if host=='owl'else 15)if expanded else 7)
 print('MC3_START',str(st),procs,flush=True);f.mc(st,procs)
print('MC3_ALL_DONE',host,len(jobs),flush=True)
