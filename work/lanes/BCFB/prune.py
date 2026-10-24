"""Retain confirmed finalists and a compact best-screen shortlist.
Archive exact text+metadata into compressed witness storage before removing
regenerable lower-ranked circuit artifacts. Never delete logs/MC/exact receipts.
"""
import os,sys
sys.dont_write_bytecode=True
import json,sqlite3,zlib
from pathlib import Path
H=Path(__file__).resolve().parent;rows=[]
for f in (H/'finalists').glob('*.screen.json'):
 r=json.loads(f.read_text());rows.append((r.get('total',1),f.name[:-len('.screen.json')],r))
rows.sort();keep={'fb_d14_c98_s517_00020','fb_d15_c105_s506_00008'};seen=set();count=0
keep.update(sys.argv[1:])
for value,stem,r in rows:
 if any((H/'finalists'/stem).with_suffix(ext).exists() for ext in ('.exact.log','.mc.log')):keep.add(stem)
 key=(round(value,12),round(r.get('exp_minus_A1',0),8))
 if key not in seen and count<12:keep.add(stem);seen.add(key);count+=1
removed=[]
with sqlite3.connect(H/'search.sqlite',timeout=120) as db:
 for value,stem,r in rows:
  if stem in keep:continue
  p=H/'finalists'/stem;q=p.with_suffix('.qasm');j=p.with_suffix('.json')
  if not(q.exists() and j.exists()):continue
  old=db.execute('select witness from prices where tag=?',(stem,)).fetchone()
  if not old:raise RuntimeError(('missing witness',stem))
  w=json.loads(zlib.decompress(old[0]));w.update(qasm=q.read_text(),metadata=json.loads(j.read_text()));db.execute('update prices set witness=? where tag=?',(zlib.compress(json.dumps(w).encode()),stem))
  removed.append(stem)
# Commit archive entries before deleting any artifacts.
for stem in removed:
 p=H/'finalists'/stem
 for ext in ('.qasm','.json','.screen.json'):p.with_suffix(ext).unlink()
out=dict(kept=sorted(keep),archived=len(removed));(H/'prune_receipt.json').write_text(json.dumps(out,indent=2));print(json.dumps(out))
