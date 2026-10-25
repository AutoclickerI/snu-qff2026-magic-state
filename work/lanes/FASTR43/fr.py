"""FASTR43 toolkit: load/emit native-tick circuits, ideal + single-fault certificate, static atom screen,
all-orders price (lane copy of MAIN's sparse_walsh with the SX-capable frontend), exact-engine speed probe.
All outputs stay in work/lanes/FASTR43."""
import os, sys
sys.dont_write_bytecode = True
for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[k] = '1'
from pathlib import Path
import json, copy, hashlib, importlib, importlib.util, subprocess, time, statistics
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
C = HERE / 'c'
C.mkdir(exist_ok=True)
sys.path[:0] = [str(HERE / 'sparse'), str(HERE), str(ROOT / 'work/lanes/FRESH'), str(ROOT / 'upstream/snu-qff2026-problem')]
import frontend as f
import circuit_io as io
import xtim
CACHE = HERE / '.xtim_cache'
CACHE.mkdir(exist_ok=True)
xtim.cache_dir = str(CACHE)
os.environ['XTIM_TWIRL_CACHE_DIR'] = str(CACHE)
PY = str(ROOT / '.venv/bin/python')
V36F = ROOT / 'work/lanes/MAIN/v36f'


def load(stem):
    stem = Path(stem)
    md = json.loads(stem.with_suffix('.json').read_text())
    ops, dets = f.parse_current(stem.with_suffix('.qasm').read_text())
    return ops, dets, md


def emit(name, ops, dets, md, recipe):
    stem = C / name
    ops = sorted(ops, key=lambda o: o.time)
    t0 = min(o.time for o in ops)
    for o in ops:
        o.time -= t0
    meta = dict(data_qubits=md['data_qubits'], cx=sum(o.kind == 'CX' for o in ops),
                native_depth=max(o.time for o in ops) + 1, recipe=recipe)
    io.emit(ops, dets, stem, meta)
    return stem


def certify(stem, singles=True):
    ops, dets, md = load(stem)
    f.DATA = md['data_qubits']
    m = f.make_model(ops, dets)
    e = f.Engine(m)
    A, N = e.ntable(0, 0)
    phi = e.phi(0)
    stabs = [e.expect(phi, (e.B.express(x), e._w(z), c)) for x, z, c in m.gen_m]
    native = [t for groups in m.steps for _, t in groups]
    r = dict(ideal_acceptance=float(A), ideal_loss=float(N[0]), stabilizers_ok=all(abs(s - 1) < 1e-10 for s in stabs),
             schedule_matches=native == [o.time for o in ops], detectors=len(dets), native_depth=max(native) + 1)
    if singles:
        c1 = 0.
        harm = []
        for fault in m.faults:
            a, n = e.ntable(fault['s'], fault['d'])
            v = 0 if n is None else fault['p'] * n[fault['e']]
            c1 += v
            if v > 1e-15:
                harm.append(fault['label'])
        r.update(c1=c1, harmful_singles=harm[:20], n_harmful=len(harm))
    r['ok'] = abs(A - 1) < 1e-10 and abs(N[0]) < 1e-10 and r['stabilizers_ok'] and r['schedule_matches'] and (not singles or not r['n_harmful'])
    Path(str(stem) + '.ideal.json').write_text(json.dumps(r, indent=2))
    return r


def atoms(stem, details=False):
    import general_atoms as g
    r = g.analyze(str(stem), details)
    Path(str(stem) + '.atoms.json').write_text(json.dumps(r, indent=1))
    return r


def price(stem, procs=10):
    stem = Path(stem).resolve()
    rel = os.path.relpath(stem, HERE / 'sparse')
    p = subprocess.run([PY, 'sparse_walsh.py', rel, '72', 'canonical', str(procs)], cwd=HERE / 'sparse',
                       capture_output=True, text=True)
    last = [l for l in p.stdout.splitlines() if l.startswith('{"source"')]
    if not last:
        raise RuntimeError(p.stderr[-3000:])
    r = json.loads(last[-1])
    Path(str(stem) + '.allorders.json').write_text(json.dumps(r, indent=2))
    return dict(loss=r.get('loss'), acceptance=r.get('acceptance'), seconds=r['seconds'])


def speed(stem, shots=20000, repeats=2):
    spec = importlib.util.spec_from_file_location('speed_predict', ROOT / 'work/lanes/XTIM/speed_predict.py')
    sp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sp)
    xtim.cache_dir = str(CACHE)
    r = sp.predict(str(stem), shots=shots, repeats=repeats)
    Path(str(stem) + '.speed.json').write_text(json.dumps(r, indent=2))
    return r


def ticks(ops):
    T = {}
    for o in ops:
        T.setdefault(o.time, []).append(o)
    return T


def show(ops, lo=0, hi=99, qs=None):
    for t in range(lo, hi + 1):
        row = [o for o in ops if o.time == t and (qs is None or set(o.qs) & set(qs))]
        if row:
            print(t, ' '.join(f"{o.kind}{'/'.join(map(str, o.qs))}" + (f"@c{o.bit}" if o.bit is not None else '') for o in row))


def find(ops, kind, qs, t):
    r = [o for o in ops if o.kind == kind and o.qs == tuple(qs) and o.time == t]
    assert len(r) == 1, (kind, qs, t, r)
    return r[0]


def collapse(ops, T, remove):
    """Remove ops `remove` (list of (kind,qs,t)) and shift every op with time > T down by one tick."""
    ops = copy.deepcopy(ops)
    for k, qs, t in remove:
        ops.remove(find(ops, k, qs, t))
    assert not [o for o in ops if o.time == T], [(o.kind, o.qs) for o in ops if o.time == T]
    for o in ops:
        if o.time > T:
            o.time -= 1
    check_conflicts(ops)
    return ops


def check_conflicts(ops):
    seen = {}
    for o in ops:
        for q in o.qs:
            assert (o.time, q) not in seen, (o.time, q, o.kind, seen[(o.time, q)])
            seen[(o.time, q)] = o.kind


def pairs_of(ops):
    """Greedy identity CX pairs: same (control,target) on consecutive ops of both qubits."""
    seq = {}
    for o in sorted(ops, key=lambda o: o.time):
        for q in o.qs:
            seq.setdefault(q, []).append(o)
    used = set()
    out = []
    for o in sorted(ops, key=lambda o: o.time):
        if o.kind != 'CX' or id(o) in used:
            continue
        a, b = o.qs
        na = seq[a][seq[a].index(o) + 1] if seq[a].index(o) + 1 < len(seq[a]) else None
        nb = seq[b][seq[b].index(o) + 1] if seq[b].index(o) + 1 < len(seq[b]) else None
        if na is not None and na is nb and na.kind == 'CX' and na.qs == o.qs and id(na) not in used:
            used.add(id(o)); used.add(id(na)); out.append((o, na))
    return out
