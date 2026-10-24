from common import *
from screen import run
import multiprocessing as mp,subprocess
manifest=json.loads((HERE/'internal_manifest.json').read_text());rows=[]
with mp.get_context('fork').Pool(16) as pool:
 for row in pool.imap_unordered(run,[x['name'] for x in manifest]):rows.append(row)
rows.sort(key=lambda x:x.get('second',1));(HERE/'internal_screen.json').write_text(json.dumps(rows,indent=1))
seen=set();selected=[]
for r in rows:
 if 'error' in r:continue
 key=(round(r['second'],12),round(r['exp_A1'],7),r['R'])
 if key in seen:continue
 seen.add(key);selected.append(r['name'])
 if len(selected)==8:break
print('shortlist',selected,flush=True)
if selected:
 p=subprocess.run([sys.executable,'batch.py',*selected],cwd=HERE);assert p.returncode==0
