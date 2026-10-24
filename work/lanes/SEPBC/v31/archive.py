"""Keep only verified finalists loose; preserve every nonfinal recipe losslessly."""
from build import *
import gzip
keep={'guard5_timing_0','guard5_timing_1','guard_joint_2'};catalog={};manifest=[]
for p in V.glob('*.plan.json'):
 name=p.name.removesuffix('.plan.json');st=V/name;c=json.loads(p.read_text());txt=st.with_suffix('.qasm').read_text();_,emitted=normalized(c)
 assert emitted==txt,name
 if name in keep:continue
 catalog[name]=dict(plan=c,qasm_sha256=hashlib.sha256(txt.encode()).hexdigest());manifest.append(name)
out=V/'nonfinal_plans.json.gz'
with gzip.open(out,'wt')as f:json.dump(catalog,f)
with gzip.open(out,'rt')as f:assert json.load(f)==catalog
for name in manifest:
 for ext in ['.qasm','.json','.plan.json']:(V/(name+ext)).unlink()
(V/'archive_manifest.json').write_text(json.dumps(dict(kept=sorted(keep),archived=sorted(manifest),exact_reemission_verified=True),indent=2));print('Kept',len(keep),'finalists; archived',len(manifest),'exact recipes')
