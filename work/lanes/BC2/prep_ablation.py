"""Exact B+C-noiseless ablation only, using MAIN/ablate.py unchanged."""
import json
import math
from pathlib import Path
import sys
import ablate

for stem in sys.argv[1:]:
    meta=json.loads(Path(stem+'.json').read_text())
    text=Path(stem+'.qasm').read_text()
    op,idle=ablate.labeller(set(meta['data_qubits']),{1,14,8,9,2,16,15},32,meta.get('round_start',50))
    ablate.model.noise_blocks=ablate.patched(lambda r:r!='prep',op,idle)
    try: c1,l2,l3,A1=ablate.score(text,meta['data_qubits'],6)
    finally: ablate.model.noise_blocks=ablate._orig
    receipt=dict(c1=c1,second=l2,third=l3,total=l2+l3,exp_minus_A1=math.exp(-A1))
    Path(stem+'.no_prep.json').write_text(json.dumps(receipt,indent=2))
    print(stem,receipt,flush=True)
