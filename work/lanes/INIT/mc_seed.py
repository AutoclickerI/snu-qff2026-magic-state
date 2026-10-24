import json
import sys
import os
from pathlib import Path
sys.path.insert(0, 'work')
from fast_check import check
n = sys.argv[1]
seed = int(sys.argv[2])
p = Path('work/lanes/INIT') / (n + '.qasm')
m = json.loads(p.with_suffix('.json').read_text())
r = check(p.read_text(), m['data_qubits'], shots=10**8, seed=seed, procs=int(os.environ.get('PROCS', '24')))
print(json.dumps({'name': n, 'seed': seed, 'score': r.score, 'sem': r.sem,
                  'acceptance': r.acceptance, 'passed': r.passed, 'n_2q': r.n_2q}), flush=True)
