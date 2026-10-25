"""End-to-end CLI wall time, ABAB order: timing.py <procs> <reps> <out.json> <stem>...
Each run is `python sparse_walsh.py <stem> 72 canonical <procs>` from EVALF/base (A) or EVALF/sparse (B), one at a
time, timed around the subprocess (interpreter start-up included); the host load average is recorded per run."""
import json, os, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
PY = str(HERE.parents[2] / '.venv/bin/python')
ENV = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
procs, reps, out = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
rows = json.loads(out.read_text()) if out.exists() else []
for stem in map(lambda s: Path(s).resolve(), sys.argv[4:]):
    for rep in range(reps):
        for d in ('base', 'sparse'):
            load = os.getloadavg()[0]
            t = time.perf_counter()
            r = subprocess.run([PY, 'sparse_walsh.py', str(stem), '72', 'canonical', procs], cwd=HERE / d, env=ENV,
                               capture_output=True, text=True)
            wall = time.perf_counter() - t
            if r.returncode:
                raise SystemExit(f'{d} {stem}: {r.stderr[-2000:]}')
            loss = json.loads(r.stdout.strip().splitlines()[-1])['loss']
            rows.append(dict(stem=stem.name, procs=int(procs), rep=rep, evaluator=d, wall=wall, load1=load, loss=loss))
            print(json.dumps(rows[-1]), flush=True)
            out.write_text(json.dumps(rows, indent=1) + '\n')
