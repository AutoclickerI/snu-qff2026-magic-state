import json,sys
from pathlib import Path
import tprep
p=Path(sys.argv[1]); m=json.loads(p.with_suffix('.json').read_text()); r=tprep.check(p.read_text(),m['data_qubits'],shots=10**6,seed=0)
print(p.stem, str(r), flush=True)
if not r.passed: raise SystemExit(1)
