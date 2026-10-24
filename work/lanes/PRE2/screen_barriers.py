import json
import os
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ENV = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
names = ['compact_narrow', 'compact_nobar', 'compact_active']
for k in (1, 2, 4, 8, 12, 16, 20, 24, 28, 32, 33):
    names += [f'compact_dropfirst{k:02d}', f'compact_droplast{k:02d}']
names += ['compact_dropeven', 'compact_dropodd', 'compact_dropedges']
rows = []
for name in names:
    q = HERE / f'{name}_m.qasm'
    if not q.exists():
        continue
    out = subprocess.run(['/home/jihoon/competitions/quantumn/.venv/bin/python', 'work/lanes/EVAL/exact2.py', str(q), '--procs', '8', '--top', '0', '--json', str(HERE / f'{name}_m.exact2.json')], cwd=HERE.parents[2], env=ENV, capture_output=True, text=True, check=True).stdout
    row = {'name': name}
    for line in out.splitlines():
        if line.startswith('second order:'):
            row['second'] = float(line.split(':', 1)[1].split()[0])
        if line.startswith('first order'):
            row['c1'] = float(line.split('=')[1].split()[0])
        if line.startswith('acceptance:'):
            row['exp_A1'] = float(line.split('exp(-A1) = ')[1].split()[0])
    rows.append(row)
    print(row, flush=True)
(HERE / 'barrier_screen.json').write_text(json.dumps(rows, indent=2) + '\n')
