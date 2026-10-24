"""Publish measured current-base improvements as atomic crossover patches."""
import sys,json,fcntl
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import pop36_support as v

def refresh():
 with (v.OUT/'patches.lock').open('w')as lock:
  fcntl.flock(lock,fcntl.LOCK_EX);file=v.OUT/'patches.json';rr=json.loads(file.read_text());known={r['name']for r in rr};by={}
  for p in v.OUT.glob('*/*.score.json'):
   r=json.loads(p.read_text())
   if not r.get('eligible')or'loss'not in r:continue
   c=v.C.read(v.H/r['stem']);by[v.d.digest(c)]=(r,c)
  added=0
  for fp,(r,c)in by.items():
   parent=r['description'].get('parent');name='crossover_'+fp
   if name in known or parent not in by or r['loss']>=by[parent][0]['loss']-1e-12:continue
   item=v.save_patch(name,by[parent][1],c,dict(family='measured_crossover',source=r['stem'],gain=by[parent][0]['loss']-r['loss']));rr.extend([item]*8);added+=1
  temp=v.OUT/'patches.next.json';temp.write_text(json.dumps(rr,indent=2));temp.replace(file)
 print('CROSSOVER_REFRESH',added,flush=True)
if __name__=='__main__':refresh()
