"""All-orders pricing for BUNDLE: MAIN/sparse evaluator called in-process (prepare -> compile_best -> 73 rows serially,
exactly sparse_walsh.run(stem, 72, canonical, 1) without its result file), many 1-process evaluations in parallel.

Cache: res/cache.jsonl, key = sha256(qasm) | ordered data_qubits | sha256 of sparse_walsh.py, frontend.py, fastfill.py,
basis_warm.json and this adapter. Empty Fourier support is a zero moment: handle
that base case before the upstream contraction, whose broadcast path rejects it.
Invalid circuits (prepare's ideal-validity assertions: noiseless acceptance 1, noiseless loss 0, or a
schedule/frontend error) are cached as errors under the same key.
"""
import os, sys, json, hashlib, time, io, contextlib
from pathlib import Path
from multiprocessing import get_context
for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[k] = '1'
H = Path(__file__).resolve().parent
SP = H / 'sparse_v37'
sys.path.insert(0, str(SP))
import sparse_walsh as sw  # noqa: E402

D = json.loads((H / 'c' / 'baseline.json').read_text())['data_qubits']
EVH = hashlib.sha256(b''.join(hashlib.sha256((SP / f).read_bytes()).digest()
                              for f in ('sparse_walsh.py', 'frontend.py', 'fastfill.py', 'basis_warm.json'))
                     + hashlib.sha256(Path(__file__).read_bytes()).digest()).hexdigest()[:16]
CACHE = H / 'res' / 'cache37.jsonl'
CDIR = H / 'c'
sw.SEARCH_WIDTH = 12
SETTINGS = {'warm':str(sw.WARM), 'width':sw.SEARCH_WIDTH}

def configure(warm, width):
    global EVH, SETTINGS
    sw.WARM=Path(warm);sw.SEARCH_WIDTH=max(12,int(width))
    SETTINGS={'warm':str(sw.WARM.relative_to(H)), 'width':sw.SEARCH_WIDTH}
    EVH=hashlib.sha256(b''.join(hashlib.sha256((SP/f).read_bytes()).digest()
        for f in ('sparse_walsh.py','frontend.py','fastfill.py'))
        +hashlib.sha256(sw.WARM.read_bytes()).digest()
        +hashlib.sha256(Path(__file__).read_bytes()).digest()
        +json.dumps(SETTINGS,sort_keys=True).encode()).hexdigest()[:16]

_TRAIN=None
def train_basis(warm):
    m,eng,groups,nd,ks=_TRAIN
    return sw.search_basis(m,eng,groups,nd,set(ks),warm)

def specialize(stem, expected):
    """Freeze an incumbent-specific exact detector basis; verify its complete price."""
    global _TRAIN
    stem=Path(stem);sha=sha_of(stem.with_suffix('.qasm').read_text())
    folder=H/'res/evaluator_bases';folder.mkdir(exist_ok=True)
    target=folder/f'{sha}.json'
    if not target.exists():
        with contextlib.redirect_stdout(io.StringIO()):
            m,eng,groups,nd,ks,*_=sw.prepare(stem,True)
        bases=json.loads(sw.WARM.read_text())
        _TRAIN=(m,eng,groups,nd,ks)
        warms=list(bases['bases'].values())
        with get_context('fork').Pool(min(5,len(warms))) as pool:
            ops,cost=min(pool.map(train_basis,warms),key=lambda r:r[1])
        keys=[','.join(map(str,sorted(d))) for d in m.dets]
        bases['bases']['POLISH_current']=[[keys[t],keys[s]] for t,s in ops]
        bases['incumbent']=sha;bases['search_width']=max(12,cost[1])
        target.write_text(json.dumps(bases,indent=2)+'\n')
    bases=json.loads(target.read_text())
    configure(target,bases['search_width'])
    k=key(sha);cache=load_cache()
    r=cache.get(k)
    if r is None:
        saved=write_stem(stem.with_suffix('.qasm').read_text())
        r=dict(price_stem(saved),key=k,stem=saved.name,configuration=dict(SETTINGS))
        with CACHE.open('a') as f:f.write(json.dumps(r)+'\n')
    assert 'loss' in r, r
    assert abs(r['loss']-expected['loss'])<1e-13 and abs(r['acceptance']-expected['acceptance'])<1e-13,(r,expected)
    print(json.dumps(dict(event='basis control',sha=sha,configuration=SETTINGS,
                         loss=r['loss'],acceptance=r['acceptance'],seconds=r['seconds'],key=k)),flush=True)
    return r

_contract = sw.contract_quotient


def contract_with_empty_support(compiled, states, emask, order):
    if len(states) == 0:
        return sw.np.empty(0, dtype=float), 0
    return _contract(compiled, states, emask, order)


sw.contract_quotient = contract_with_empty_support


def key(sha, dq=D):
    return f"{sha}|{','.join(map(str, dq))}|{EVH}"


def load_cache():
    out = {}
    if CACHE.exists():
        for l in CACHE.read_text().splitlines():
            try:
                r = json.loads(l)
                out[r['key']] = r
            except Exception:
                pass
    return out


def sha_of(text):
    return hashlib.sha256(text.encode()).hexdigest()


def write_stem(text, dq=D):
    s = sha_of(text)
    st = CDIR / s[:24]
    if not st.with_suffix('.qasm').exists():
        st.with_suffix('.json').write_text(json.dumps(dict(data_qubits=dq)))
        st.with_suffix('.qasm').write_text(text)
    return st


def price_stem(st, nkeys=72):
    """Serial all-orders price of one stem; returns dict(loss, acceptance, bound, width, seconds) or dict(error)."""
    t = time.perf_counter()
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            m, eng, groups, nd, ks, psi, where, de = sw.prepare(Path(st), True)
            compiled, elim = sw.compile_best(m, eng, groups, nd, ks)
            keys = [None] + eng.keys[:nkeys]
            sw._CTX.update(eng=eng, ks=ks, psi=psi, where=where, compiled=compiled, elim=elim)
            rows = [sw._row(k) for k in keys]
        A = rows[0]['value']
        obs = sum(w * b * r['value'] for w, b, r in zip(eng.W, eng.beta, rows[1:]))
        eA = rows[0]['absolute_kernel_omission_bound']
        eO = sum(abs(w * b) * r['absolute_kernel_omission_bound'] for w, b, r in zip(eng.W, eng.beta, rows[1:]))
        return dict(loss=(A - obs) / (2 * A), acceptance=A, bound=eO / (2 * (A - eA)) + abs(obs) * eA / (2 * A * (A - eA)),
                    width=elim['width'], seconds=time.perf_counter() - t)
    except Exception as e:
        return dict(error=repr(e)[:200], seconds=time.perf_counter() - t)


def _price_job(args):
    k, text = args
    st = write_stem(text)
    r = price_stem(st)
    r['key'] = k
    r['stem'] = st.name
    r['configuration'] = dict(SETTINGS)
    return r


if __name__ == '__main__':
    # usage: ev.py <stem> : price one stem (absolute or relative path, no suffix) at one process
    st = Path(sys.argv[1])
    print(json.dumps(price_stem(st)))
