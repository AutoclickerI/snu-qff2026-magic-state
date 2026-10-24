"""Cross over measured improvements and current external menu recipes."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));import pop35_support as v,pop35_moves as m
rr=[]
for name,p,desc in v.external_patches():rr.append(dict(name=name,description=desc,patch={key:sorted([list(x)if isinstance(x,tuple)else x for x in val],key=str)for key,val in p.items()}))
byfp={}
for p in v.OUT.glob('*/*.score.json'):
 r=json.loads(p.read_text())
 if not r.get('eligible')or'loss'not in r:continue
 c=v.C.read(v.H/r['stem']);byfp[v.d.digest(c)]=(r,c)
for fp,(r,c)in byfp.items():
 parent=r['description'].get('parent')
 if parent not in byfp or r['loss']>=byfp[parent][0]['loss']-1e-12:continue
 p=v.k.patches(byfp[parent][1],c);item=dict(name='crossover_'+fp,description=dict(family='measured_crossover',source=r['stem'],gain=byfp[parent][0]['loss']-r['loss']),patch={key:sorted([list(x)if isinstance(x,tuple)else x for x in val],key=str)for key,val in p.items()});rr.extend([item]*8)
# The useful q7 X child came from a shorter window than WAITPROT's Z gadget.
# Explicitly cross its late-helper instrument with that measured Z recipe.
for fp,(r,c)in sorted(byfp.items(),key=lambda z:z[1][0]['loss'])[:5]:
 for g in m.guards(c):
  if g['q']!=7 or g['h']!=13 or g['times'][0]<25:continue
  x=m.drop(c,g);h=13;b=v.C.bit(x)
  for t,ls in [(26,['reset q[13];','h q[13];']),(27,['cx q[13],q[7];']),(31,['cx q[13],q[7];']),(32,['h q[13];',f'measure q[13] -> c[{b}];','h q[13];'])]:x['u'].append(v.C.Unit(ls));x['t'].append(t)
  x['tail'].append(f'// DETECTOR c[{b}]')
  try:x=v.d.normalize(x)
  except Exception:continue
  p=v.k.patches(c,x);item=dict(name='q7_Z_rebuild_'+fp,description=dict(family='q7_rebuild',source=r['stem']),patch={key:sorted([list(xx)if isinstance(xx,tuple)else xx for xx in val],key=str)for key,val in p.items()});rr.extend([item]*20)
priority=[r for r in rr if r['name'].startswith('released_q7')];(v.OUT/'patches.json').write_text(json.dumps(priority*20+rr,indent=2));print('PATCHES',len(rr),'q7',len(priority),'measured population',len(byfp))
