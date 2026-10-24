"""Add only measured, useful complete-circuit native crossovers to the menu."""
import sys,json,fcntl
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import pop36_support as v
with (v.OUT/'patches.lock').open('w')as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);rr=json.loads((v.OUT/'patches.json').read_text());known={r['name']for r in rr};good=[]
 for p in v.OUT.glob('*/*.score.json'):
  r=json.loads(p.read_text())
  if r.get('eligible')and'loss'in r:good.append(r)
 good.sort(key=lambda r:r['loss']);added=0
 # A measured whole-circuit crossover translates an alternate island's
 # endpoint into the local current best and is repriced with any later edits.
 if good:
  parents=good[:3]
  for pr in parents:
   pc=v.C.read(v.H/pr['stem']);pf=v.d.digest(pc)
   for r in good[:8]:
    if r['loss']>=pr['loss']-1e-12:continue
    c=v.C.read(v.H/r['stem']);fp=v.d.digest(c);name='cross_host_'+pf+'_'+fp
    if name in known:continue
    rr.extend([v.save_patch(name,pc,c,dict(family='cross_host',source=r['stem'],parent=pr['stem']))]*4);known.add(name);added+=1
 p=v.OUT/'patches.next.json';p.write_text(json.dumps(rr,indent=2));p.replace(v.OUT/'patches.json')
print('CROSS_HOST_PATCHES',added)
