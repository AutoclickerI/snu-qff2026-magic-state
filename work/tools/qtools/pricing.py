"""Versioned, process-safe all-orders prices. No sampled acceptance gate."""
import hashlib
import json
import math
from pathlib import Path
import threading
import time
from .stems import read_stem
from .storage import atomic_json, locked
from .version import EVALUATOR_VERSION, TOOLS, evaluator_version

CACHE = TOOLS / 'cache' / 'prices'
_ENGINE_LOCK = threading.Lock()  # frontend.DATA and contraction context are process globals


class InvalidCircuit(ValueError):
    def __init__(self, raw):
        self.raw = raw
        super().__init__('raw correctness failed: ' + '; '.join(raw['errors']))


def cache_key(qasm_sha256, data_qubits, version):
    return hashlib.sha256(json.dumps([qasm_sha256, list(data_qubits), version],
                                    separators=(',', ':')).encode()).hexdigest()


def _calculate(qasm, data, processes, *, registry=None, save_basis=True):
    from .validity import raw_check
    from .evaluator import sparse_walsh as sw
    raw = raw_check(qasm.decode(), data)
    if not raw['ok']:
        raise InvalidCircuit(raw)
    with _ENGINE_LOCK:
        m, eng, groups, nd, ks, psi, where, _ = sw.prepare(
            None, True, text=qasm.decode(), data_qubits=data)
        compiled, elim = sw.compile_best(m, eng, groups, nd, ks, registry=registry, save=save_basis)
        sw._CTX.update(eng=eng, ks=ks, psi=psi, where=where, compiled=compiled, elim=elim)
        try:
            keys = [None] + eng.keys
            if processes == 1:
                rows = [sw._row(k) for k in keys]
            else:
                import multiprocessing as mp
                # Caller plus workers never exceeds the requested process budget.
                with mp.get_context('fork').Pool(processes - 1) as pool:
                    rows = list(pool.imap(sw._row, keys))
            A = rows[0]['value']
            obs = sum(w * b * r['value'] for w, b, r in zip(eng.W, eng.beta, rows[1:]))
            loss = (A - obs) / (2 * A)
            eA = rows[0]['absolute_kernel_omission_bound']
            eO = sum(abs(w * b) * r['absolute_kernel_omission_bound']
                     for w, b, r in zip(eng.W, eng.beta, rows[1:]))
            if not all(math.isfinite(v) for v in (A, loss)) or A <= eA:
                raise ArithmeticError('nonfinite price or acceptance below kernel error bound')
            return dict(loss=float(loss), acceptance=A, width=elim['width'], basis=elim['basis'], raw=raw,
                        exact_acceptance_ok=A >= .5002,
                        kernel_omission_bound=float(eO / (2 * (A-eA)) + abs(obs)*eA/(2*A*(A-eA))))
        finally:
            sw._CTX.clear()
            sw.COLUMNS.clear()


def price(stem, processes=1, *, use_cache=True):
    """Return an exact price or raise InvalidCircuit; seconds is this call's wall time.

    evaluation_seconds retains the measured miss time on a hit. Numerical source changes
    require a process restart, preventing old loaded functions being labeled with a new hash.
    """
    start = time.perf_counter()
    if type(processes) is not int or processes < 1:
        raise ValueError('processes must be a positive integer')
    if evaluator_version() != EVALUATOR_VERSION:
        raise RuntimeError('qtools sources changed: restart this process before pricing')
    qasm, data = read_stem(stem)
    sha = hashlib.sha256(qasm).hexdigest()
    metadata = dict(qasm_sha256=sha, data_qubits=list(data), evaluator_version=EVALUATOR_VERSION)
    key = cache_key(sha, data, EVALUATOR_VERSION)
    target = CACHE / (key + '.json')
    with locked(CACHE / (key + '.lock')):
        if use_cache and target.exists():
            result = json.loads(target.read_bytes())
            if any(result[k] != v for k, v in metadata.items()):
                raise ValueError('cache identity mismatch: ' + str(target))
            return dict(result, cache_hit=True, seconds=time.perf_counter() - start)
        result = dict(_calculate(qasm, data, processes), **metadata)
        elapsed = time.perf_counter() - start
        result.update(seconds=elapsed, evaluation_seconds=elapsed, cache_hit=False)
        atomic_json(target, result)
        return result
