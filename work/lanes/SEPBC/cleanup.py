"""Remove nonfinal circuit artifacts after the consolidated receipts exist."""
import json,shutil,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent
assert (H/'measurements.jsonl').exists()and(H/'finalist_manifest.json').exists()
keep={'REPORT.md','built_variants.csv','measurements.jsonl','solver_receipts.json','finalist_manifest.json','static_certificate.json','static_certificate_7.json','q5_pair_delta.json','separate_provenance.json','separate_speed.json'}
removed=[]
for p in H.iterdir():
 if p.is_file()and not(p.suffix=='.py'or p.name in keep or p.name.startswith(('best.','nonblue.'))):removed.append(p.name);p.unlink()
for name in('.xtim_cache','third_cache','__pycache__'):
 p=H/name
 if p.exists():shutil.rmtree(p)
for p in(H/'audit').glob('*_result.json'):p.unlink()
for p in(H/'inputs').glob('*.exact*'):p.unlink()
for p in(H/'inputs').glob('*.price.json'):p.unlink()
manifest=json.loads((H/'finalist_manifest.json').read_text())
for name,files in manifest['files'].items():
 for suffix,sha in files.items():assert hashlib.sha256((H/(name+suffix)).read_bytes()).hexdigest()==sha
print(json.dumps(dict(removed_root_files=len(removed),finalist_hashes_verified=True)))
