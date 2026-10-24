"""CLI: restore_variant.py NAME. Re-emits into SEPBC/v31/restored/ only."""
from build import *
import gzip
name=sys.argv[1]
with gzip.open(V/'nonfinal_plans.json.gz','rt')as f:row=json.load(f)[name]
(V/'restored').mkdir(exist_ok=True);st=save(row['plan'],'v31/restored/'+name)
assert hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest()==row['qasm_sha256']
print(st)
