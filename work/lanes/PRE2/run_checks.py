import json, os
from pathlib import Path
import sys
sys.path.insert(0, '/home/jihoon/competitions/quantumn/work')
import fast_check

HERE = Path(__file__).resolve().parent
names = ['v14_narrow_m', 'v14_nobar_m', 'compact_narrow_m', 'compact_dropcombo_16_31_32_m', 'no_step20_m', 'inject_only_m']
os.environ.update(OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
for name in names:
    text = (HERE / f'{name}.qasm').read_text()
    data = json.loads((HERE / f'{name}.json').read_text())['data_qubits']
    rep = fast_check.check(text, data, shots=10**6, seed=0, procs=8)
    out = {'score': float(rep.score), 'sem': float(rep.sem), 'acceptance': float(rep.acceptance),
           'n_2q': int(rep.n_2q), 'passed': bool(rep.passed), 'format': bool(rep.format_ok),
           'class': bool(rep.class_ok), 'correctness': bool(rep.correct_ok), 'acceptance_ok': bool(rep.acceptance_ok)}
    (HERE / f'{name}.check.json').write_text(json.dumps(out, indent=2) + '\n')
    print(name, out, flush=True)
