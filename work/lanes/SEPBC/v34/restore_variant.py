"""CLI: restore_variant.py NAME; emits into SEPBC/v34/restored/."""
from design import *
import gzip
name=sys.argv[1]
with gzip.open(V/'nonfinal_plans.json.gz','rt')as f:row=json.load(f)[name]
(V/'restored').mkdir(exist_ok=True);st=save(row['plan'],'v34/restored/'+name)
assert hashlib.sha256(st.with_suffix('.qasm').read_bytes()).hexdigest()==row['qasm_sha256'];print(st)
