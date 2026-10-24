"""Gate a priced stem: copy to INTEG/<out>.{qasm,json}, judge 1e6 (fast_check), FRESH speed screen.

finalize.py <stem under c/> <out name>
"""
import json, subprocess, sys, os, shutil, re
from pathlib import Path
H = Path(__file__).resolve().parent
ROOT = H.parents[2]
st, out = sys.argv[1], sys.argv[2]
src = H / 'c' / st
res = json.loads((H / 'res' / (st + '.json')).read_text())
meta = json.loads(src.with_suffix('.json').read_text())
base_meta = json.loads((ROOT / 'work/lanes/MAIN/v36c.json').read_text())
assert meta['data_qubits'] == base_meta['data_qubits']
shutil.copy(src.with_suffix('.qasm'), H / (out + '.qasm'))
(H / (out + '.json')).write_text(json.dumps(dict(data_qubits=meta['data_qubits'], cx=meta.get('cx'), native_depth=meta.get('native_depth'),
                                                  R=base_meta.get('R'), source=f'INTEG {st}', integ=meta.get('integ')), indent=2))
env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
j = subprocess.run([str(ROOT / '.venv/bin/python'), 'fast_check.py', str(H / (out + '.qasm')), str(H / (out + '.json')), '1000000', '1'],
                   cwd=ROOT / 'work', capture_output=True, text=True, env=env)
s = subprocess.run([str(ROOT / '.venv/bin/python'), '-B', 'work/lanes/FRESH/general_atoms.py', str(H / out)],
                   cwd=ROOT, capture_output=True, text=True, env=env)
rec = dict(name=out, stem=st, loss=res['loss'], acceptance=res['acceptance'], cx=meta.get('cx'),
           judge=j.stdout.strip()[-600:], judge_err=j.stderr.strip()[-300:], speed=s.stdout.strip()[-400:], speed_err=s.stderr.strip()[-300:])
rec['passed'] = 'passed=True' in j.stdout or "'passed': True" in j.stdout or '"passed": true' in j.stdout
rec['fast'] = '"FAST"' in s.stdout or "FAST" in s.stdout
f = H / 'finalists.json'
allr = json.loads(f.read_text()) if f.exists() else {}
allr[out] = rec
f.write_text(json.dumps(allr, indent=1))
print(json.dumps(rec, indent=1))
