"""Retain completed finalists; compress inactive generated circuit witnesses."""
from pathlib import Path
import tarfile,json,hashlib
H=Path(__file__).resolve().parent
keep={'st1_final','st1_r38_a','st1_r38_b','st1_boundary_d','v25k_exchange4','v25k_exchange4_feedback_best','combined_endpoint_instrument15_alap','v23h_c2c9_exchange4'}
files=[]
for p in sorted(H.glob('*.qasm')):
 if p.stem in keep:continue
 for f in H.glob(p.stem+'.*'):
  if f.is_file()and not f.name.endswith(('.gz','.xz','.tar')):files.append(f)
files=sorted(set(files));manifest=[dict(name=f.name,size=f.stat().st_size,sha256=hashlib.sha256(f.read_bytes()).hexdigest())for f in files];archive=H/'inactive_circuit_witnesses_final.tar.gz'
assert not archive.exists()
with tarfile.open(archive,'w:gz')as tar:
 for f in files:tar.add(f,arcname=f.name,recursive=False)
with tarfile.open(archive,'r:gz')as tar:
 assert len(tar.getmembers())==len(files)
 for r in manifest:assert hashlib.sha256(tar.extractfile(r['name']).read()).hexdigest()==r['sha256']
for f,r in zip(files,manifest):
 assert hashlib.sha256(f.read_bytes()).hexdigest()==r['sha256'];f.unlink()
(H/'inactive_circuit_witnesses_final.manifest.json').write_text(json.dumps(manifest,indent=1));print(json.dumps(dict(files=len(files),archive=str(archive),bytes=archive.stat().st_size)))
