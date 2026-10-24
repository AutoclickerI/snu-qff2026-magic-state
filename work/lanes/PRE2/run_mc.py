import json, os, re, subprocess, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = '/home/jihoon/competitions/quantumn/.venv/bin/python'
names = ['v14_narrow_m', 'v14_nobar_m', 'compact_narrow_m', 'compact_dropcombo_16_31_32_m']
seeds = [0, 1000, 2000]
env = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
rows = []
for name in names:
    for seed in seeds:
        ncpu = os.cpu_count() or 1
        load = float(open('/proc/loadavg').read().split()[0])
        if load > 0.75 * ncpu:
            raise RuntimeError(f'load {load} exceeds 75% of {ncpu} before {name} seed {seed}')
        t0 = time.time()
        cmd = [PY, 'work/fast_check.py', str(HERE / f'{name}.qasm'), str(HERE / f'{name}.json'), '100000000', '8']
        # fast_check CLI has a fixed seed=0; set the requested seed through this small wrapper.
        code = ('import sys; sys.path.insert(0, "work"); import fast_check; '
                f't=open("{HERE / (name + ".qasm")}").read(); import json; '
                f'd=json.load(open("{HERE / (name + ".json")}"))["data_qubits"]; '
                f'r=fast_check.check(t,d,shots=10**8,seed={seed},procs=8); '
                'print(json.dumps({"score":float(r.score),"sem":float(r.sem),"acceptance":float(r.acceptance),"n_2q":int(r.n_2q),"passed":bool(r.passed)}))')
        p = subprocess.run([PY, '-c', code], cwd=HERE.parents[2], env=env, capture_output=True, text=True, check=True)
        line = p.stdout.strip().splitlines()[-1]
        rep = json.loads(line)
        rep.update(name=name, seed=seed, seconds=time.time() - t0)
        rows.append(rep)
        print(rep, flush=True)
(HERE / 'mc_results.json').write_text(json.dumps(rows, indent=2) + '\n')
for name in names:
    vals = [r['score'] for r in rows if r['name'] == name]
    print(name, 'mean', sum(vals) / len(vals), flush=True)
