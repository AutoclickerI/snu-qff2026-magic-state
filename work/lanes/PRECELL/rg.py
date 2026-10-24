"""Run region.py counterfactuals for several specs sequentially: rg.py <stem> <procs> spec.json ... (stem relative to MAIN/sparse)."""
import os, sys, json
for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[k] = '1'
from pathlib import Path
H = Path(__file__).resolve().parent
SP = H.parent / 'MAIN' / 'sparse'
sys.path.insert(0, str(SP))
os.chdir(SP)
import region
stem, procs = sys.argv[1], int(sys.argv[2])
for f in sys.argv[3:]:
    spec = json.loads(Path(f).read_text())
    region.run(stem, spec, procs)
