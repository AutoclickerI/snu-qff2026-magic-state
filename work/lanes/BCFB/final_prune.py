"""Archive every non-finalist circuit before retaining only measured finalists."""
import json,sqlite3,zlib
from pathlib import Path
H=Path(__file__).resolve().parent
assert json.loads((H/'RUN_SUMMARY.json').read_text())['status']=='ALL_REQUESTED_BUDGETS_COMPLETE'
keep=set(json.loads((H/'redraw_manifest.json').read_text()));rd=json.loads((H/'redraw_summary.json').read_text());assert all(rd[k]['complete100'] for k in keep)
remove=[]
with sqlite3.connect(H/'search.sqlite',timeout=120) as db:
 for q in (H/'finalists').glob('*.qasm'):
  if q.stem in keep:continue
  j=q.with_suffix('.json');r=db.execute('select witness from prices where tag=?',(q.stem,)).fetchone();assert r and j.exists(),q
  w=json.loads(zlib.decompress(r[0]));w.update(qasm=q.read_text(),metadata=json.loads(j.read_text()));db.execute('update prices set witness=? where tag=?',(zlib.compress(json.dumps(w).encode()),q.stem));remove.append(q)
for q in remove:
 for suffix in ('.qasm','.json','.screen.json'):q.with_suffix(suffix).unlink(missing_ok=True)
print('Kept',len(keep),'finalists; archived',len(remove),'other circuit texts')
