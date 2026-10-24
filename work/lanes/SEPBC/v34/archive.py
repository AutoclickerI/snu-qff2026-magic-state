"""Keep verified finalists; retain exact plans for all nonfinal constructions."""
from design import *
import gzip
keep={'checked16_timing_0','layer26_timing_0','layer_26_R44_m2'};catalog={}
for p in V.glob('*.plan.json'):
 name=p.name.removesuffix('.plan.json')
 if name in keep:continue
 c=json.loads(p.read_text());txt=(V/(name+'.qasm')).read_text();_,same=normalized(c);assert txt==same,name
 catalog[name]=dict(plan=c,qasm_sha256=hashlib.sha256(txt.encode()).hexdigest(),priced=(V/(name+'.allorders.json')).exists())
with gzip.open(V/'nonfinal_plans.json.gz','wt')as f:json.dump(catalog,f)
with gzip.open(V/'nonfinal_plans.json.gz','rt')as f:assert json.load(f)==catalog
for n in catalog:
 for ext in ['.qasm','.json','.plan.json']:(V/(n+ext)).unlink()
(V/'archive_manifest.json').write_text(json.dumps(dict(kept=sorted(keep),archived=sorted(catalog),exact_reemission_verified=True),indent=2));print('Archived',len(catalog),'nonfinal plans; kept',len(keep),'finalists')
