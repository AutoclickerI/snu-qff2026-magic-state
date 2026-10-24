from a30_common import *
import sqlite3,zlib,subprocess,concurrent.futures
rows=[]
for name in ['feedback_neighbors','full_masks']:
 db=sqlite3.connect(f'file:{D/name}.sqlite?mode=ro',uri=True)
 for i,r,q,m in db.execute('select id,row,qasm,md from results'):
  r=json.loads(r)
  if r.get('exp_minus_A1',0)<.5002 or r.get('total',1)>5.82394e-5:continue
  md=json.loads(m);reuse=md['options']['spec']['reuse']
  if 2 in reuse:continue
  rows.append((r['total'],name,i,r,q,m))
seen=set();chosen=[]
for value,name,i,r,q,m in sorted(rows):
 key=(round(value,13),round(r['exp_minus_A1'],9))
 if key in seen:continue
 seen.add(key);stem=D/'finalists'/f'a30_fastpick_{name}_{i:05}';stem.with_suffix('.qasm').write_text(zlib.decompress(q).decode());stem.with_suffix('.json').write_text(m);stem.with_suffix('.screen.json').write_text(json.dumps(r,indent=2));chosen.append(str(stem))
 if len(chosen)==12:break
(D/'fastpick_manifest.json').write_text(json.dumps(chosen,indent=2))
def run(stem):
 with (D/'runs'/(Path(stem).name+'.probe.log')).open('w') as log:r=subprocess.run([sys.executable,str(H/'a30_speed.py'),stem,'--probe'],cwd=D,stdout=log,stderr=subprocess.STDOUT)
 speed=json.loads(Path(stem+'.speed.json').read_text());print(Path(stem).name,r.returncode,speed['classification'],speed['median_seconds_per_1e6'],flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=6) as e:list(e.map(run,chosen))
