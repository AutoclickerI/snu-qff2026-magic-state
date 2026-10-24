import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import acceptance as a
import protection_budget as p,budget_feedback as f,a_resource_port as ar
out=a.OUT/'prepared';out.mkdir(exist_ok=True);jobs=[];errors=[]
for kind in sys.argv[1:]:
 try:
  if kind=='cross':items=p.cross_seeds()
  elif kind=='feedback':items=f.proposals(a.d.normalize(a.C.read(a.OUT/'base')),'v32p')
  elif kind=='A':
   c=ar.port(a.d.normalize(a.C.read(a.OUT/'base')));items=[]if c is None else [('bcfb_A_R45',c,dict(family='BCFB_A_port',pivots=[1,14,9,2]))]
  for name,c,desc in items:
   st=out/name;a.d.save(c,st);jobs.append((str(st),desc));print('built',name,flush=True)
 except Exception as e:errors.append(dict(kind=kind,error=repr(e)));print(kind,repr(e),flush=True)
(out/'queue.json').write_text(json.dumps(jobs,indent=2));(out/'errors.json').write_text(json.dumps(errors,indent=2));print('DONE',len(jobs),errors,flush=True)
