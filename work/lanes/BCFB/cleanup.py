"""Remove only archived bulk and abandoned experimental helpers."""
import json,hashlib,shutil
from pathlib import Path
H=Path(__file__).resolve().parent
arc=json.loads((H/'ARCHIVE_AUDIT.json').read_text());assert arc['status']=='PASS'
assert hashlib.file_digest((H/'witnesses.tar.xz').open('rb'),'sha256').hexdigest()==arc['sha256']
assert json.loads((H/'SEED0_VERIFICATION.json').read_text())['passed']
archived=set(arc['archived_evidence']);removed=[]
for f in sorted((H/'runs').glob('*')):
 if not f.is_file():continue
 if f.name.startswith('redraw') or '_redraw_' in f.name:continue
 assert 'evidence/runs/'+f.name in archived,f
 f.unlink();removed.append(str(f.relative_to(H)))
for f in sorted(H.glob('*.log')):
 if f.name.startswith('best_seed0'):continue
 assert 'evidence/logs/'+f.name in archived,f
 f.unlink();removed.append(f.name)
for n in ('moments_vector.py','validate_vector.py','cache_audit.py','signature.py','stop_for_upgrade.py','read_prior_logs.py','import_prior.py'):
 f=H/n
 if f.exists():assert 'evidence/experimental_code/'+n in archived;f.unlink();removed.append(n)
for n in ('replay.qasm','replay.json'):
 f=H/'inputs'/n
 if f.exists():assert 'evidence/inputs/'+n in archived;f.unlink();removed.append('inputs/'+n)
for f in H.glob('*.sqlite*'):f.unlink();removed.append(f.name)
for p in (H/'__pycache__',H/'.xtim_cache'):
 if p.exists():shutil.rmtree(p);removed.append(p.name)
(H/'CLEANUP.json').write_text(json.dumps(dict(status='COMPLETE',archived_bulk_removed=len(removed),removed=removed),indent=2));print(len(removed),'archived bulk files removed')
