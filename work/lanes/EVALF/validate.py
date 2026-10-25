"""Validate EVALF/sparse against EVALF/base (a copy of MAIN/sparse) end to end: validate.py <procs> <out.json> <stem>...
For each stem: both CLIs (`sparse_walsh.py <stem> 72 canonical <procs>`, run to exit one after the other), then
modelcheck.py. Records per-moment max |delta|, delta loss, delta acceptance, kernel sizes, omission bounds, seconds."""
import json, os, subprocess, sys, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
PY = str(HERE.parents[2] / '.venv/bin/python')
ENV = dict(os.environ, OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1', MKL_NUM_THREADS='1')
procs, out = sys.argv[1], Path(sys.argv[2])
rows = json.loads(out.read_text()) if out.exists() else {}
for stem in map(lambda s: Path(s).resolve(), sys.argv[3:]):
    res = {}
    for d in ('base', 'sparse'):
        t = time.perf_counter()
        r = subprocess.run([PY, 'sparse_walsh.py', str(stem), '72', 'canonical', procs], cwd=HERE / d, env=ENV,
                           capture_output=True, text=True)
        if r.returncode:
            raise SystemExit(f'{d} {stem}: {r.stderr[-2000:]}')
        res[d] = json.loads((HERE / d / f'{stem.name}_canonical_sparse_result.json').read_text())
        res[d]['wall'] = time.perf_counter() - t
    b, n = res['base'], res['sparse']
    vb = [r['value'] for r in b['results']]; vn = [r['value'] for r in n['results']]
    assert [r['key'] for r in b['results']] == [r['key'] for r in n['results']]
    mc = subprocess.run([PY, str(HERE / 'modelcheck.py'), str(stem)], env=ENV, capture_output=True, text=True)
    if mc.returncode:
        raise SystemExit(f'modelcheck {stem}: {mc.stderr[-2000:]}')
    rows[stem.name] = dict(
        moments=len(vb), max_abs_moment_delta=max(abs(x - y) for x, y in zip(vb, vn)),
        loss_base=b['loss'], loss_new=n['loss'], delta_loss=n['loss'] - b['loss'],
        acceptance_base=b['acceptance'], delta_acceptance=n['acceptance'] - b['acceptance'],
        kernel_nonzero_same=[r['kernel_nonzero'] for r in b['results']] == [r['kernel_nonzero'] for r in n['results']],
        omission_bound_base=b['conditional_loss_kernel_omission_bound'],
        omission_bound_new=n['conditional_loss_kernel_omission_bound'],
        width=n['conditioned_width'], width_base=b['conditioned_width'], dense_width=n['dense_width'],
        dense_width_base=b['dense_width'], wall_base=b['wall'], wall_new=n['wall'],
        model=json.loads(mc.stdout.strip().splitlines()[-1]))
    print(json.dumps({stem.name: rows[stem.name]}), flush=True)
    out.write_text(json.dumps(rows, indent=1) + '\n')
