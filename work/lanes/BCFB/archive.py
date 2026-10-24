"""One compressed witness archive; no loose bulk prep/circuit outputs."""
import os,sys
sys.dont_write_bytecode=True
import json,sqlite3,zlib,tarfile,io,csv,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
assert (H/'RUN_SUMMARY.json').exists(), 'Freeze the completed run summary before final archival'
p=H/'witnesses.tar.xz';tmp=H/'witnesses.new.tar.xz';count=0
with sqlite3.connect(H/'search.sqlite') as db,tarfile.open(tmp,'w:xz') as tar,(H/'search.csv').open('w') as out:
 w=csv.DictWriter(out,fieldnames=['tag','kind','status','c1','second','third','total','exp_minus_A1','CX','R','seconds','error']);w.writeheader()
 for tag,kind,value,row,witness in db.execute('select * from prices order by tag'):
  r=json.loads(row);r.update(tag=tag,kind=kind);w.writerow({k:r.get(k,'') for k in w.fieldnames});b=zlib.decompress(witness);t=tarfile.TarInfo('witnesses/'+tag+'.json');t.size=len(b);tar.addfile(t,io.BytesIO(b));count+=1
  b=row.encode();t=tarfile.TarInfo('receipts/'+tag+'.json');t.size=len(b);tar.addfile(t,io.BytesIO(b))
 for f in sorted((H/'runs').glob('*')):
  if f.is_file():tar.add(f,arcname='evidence/runs/'+f.name,recursive=False)
 for f in sorted(H.glob('*.log')):tar.add(f,arcname='evidence/logs/'+f.name,recursive=False)
 for f in sorted((H/'inputs').glob('*')):
  if f.is_file():tar.add(f,arcname='evidence/inputs/'+f.name,recursive=False)
 for name in ('moments_vector.py','validate_vector.py','cache_audit.py','signature.py','stop_for_upgrade.py','read_prior_logs.py','import_prior.py'):
  f=H/name
  if f.exists():tar.add(f,arcname='evidence/experimental_code/'+name,recursive=False)
 os.fsync(out.fileno())
tmp.replace(p);print(json.dumps(dict(witnesses=count,archive=str(p),bytes=p.stat().st_size)))
