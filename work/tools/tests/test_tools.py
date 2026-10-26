from concurrent.futures import ProcessPoolExecutor
import copy
import hashlib
import json
from pathlib import Path
import shutil
import time

import pytest
from qtools import (InvalidCircuit, expected_key_delta, identity, is_finalist,
                    price, raw_check, write_stem)
from qtools.pricing import cache_key
from qtools.registry import add_basis, basis_id, load_registry
from qtools.version import EVALUATOR_VERSION, PACKAGE, TOOLS, evaluator_version

MAIN = TOOLS / 'tests' / 'fixtures'
D = [6, 20, 19, 10, 2, 22, 16]


def _write(args):
    text, data, directory = args
    return str(write_stem(text, data, directory, 'parallel'))


def _add(args):
    ops, path = args
    return add_basis(ops, source='concurrency test', path=path)


def _price(args):
    return price(args)


def test_stem_identity_and_output_order(tmp_path):
    text = (MAIN / 'v37h.qasm').read_text()
    a = write_stem(text, D, tmp_path, 'test', source='fixture')
    stamp = a.with_suffix('.qasm').stat().st_mtime_ns
    assert write_stem(text, D, tmp_path, 'test') == a
    assert a.with_suffix('.qasm').stat().st_mtime_ns == stamp
    b = write_stem(text, D[::-1], tmp_path, 'test')
    sha = hashlib.sha256(text.encode()).hexdigest()
    assert a.name == 'test_' + sha[:16] + '_d' + '_'.join(map(str, D))
    assert a != b and identity(a) == (sha, tuple(D)) and identity(b) == (sha, tuple(D[::-1]))
    a.with_suffix('.json').write_text(json.dumps({'data_qubits': D[::-1]}))
    with pytest.raises(ValueError, match='collision'):
        write_stem(text, D, tmp_path, 'test')


def test_atomic_parallel_writes(tmp_path):
    # Two workers only; the controller is idle while waiting.
    text = (MAIN / 'v37h.qasm').read_text()
    with ProcessPoolExecutor(max_workers=2) as pool:
        paths = list(pool.map(_write, [(text, D, tmp_path)] * 8))
    assert len(set(paths)) == 1
    assert identity(paths[0]) == (hashlib.sha256(text.encode()).hexdigest(), tuple(D))
    registry = tmp_path / 'bases.json'
    shutil.copyfile(TOOLS / 'bases.json', registry)
    programs = [[['1', str(i)]] for i in range(2, 10)]
    with ProcessPoolExecutor(max_workers=2) as pool:
        list(pool.map(_add, [(ops, registry) for ops in programs]))
    saved = load_registry(registry)['bases']
    assert all(saved[basis_id(ops)] == ops for ops in programs)


def test_source_change_invalidates_cache_key(tmp_path):
    package = tmp_path / 'qtools'
    shutil.copytree(PACKAGE, package, ignore=shutil.ignore_patterns('__pycache__'))
    before = evaluator_version(package)
    assert before == EVALUATOR_VERSION
    with (package / 'evaluator/frontend.py').open('a') as stream:
        stream.write('\n# deliberate source edit\n')
    after = evaluator_version(package)
    assert after != before
    sha, data = identity(MAIN / 'v37i')
    assert len({cache_key(sha, data, before), cache_key(sha, data, after),
                cache_key(sha, data[::-1], before), cache_key('0'*64, data, before)}) == 4


def test_cache_never_crosses_identity(tmp_path, monkeypatch):
    import qtools.pricing as pricing
    monkeypatch.setattr(pricing, 'CACHE', tmp_path / 'prices')
    calls = []
    def calculate(qasm, data, processes):
        calls.append((qasm, data))
        return dict(loss=.001, acceptance=.6, width=1, basis={})
    monkeypatch.setattr(pricing, '_calculate', calculate)
    a = write_stem('test QASM bytes', D, tmp_path, 'a')
    b = write_stem('test QASM bytes', D[::-1], tmp_path, 'a')
    c = write_stem('different QASM bytes', D, tmp_path, 'a')
    assert not price(a)['cache_hit'] and price(a)['cache_hit']
    assert not price(b)['cache_hit'] and not price(c)['cache_hit']
    monkeypatch.setattr(pricing, 'EVALUATOR_VERSION', 'changed evaluator')
    monkeypatch.setattr(pricing, 'evaluator_version', lambda: 'changed evaluator')
    assert not price(a)['cache_hit'] and price(a)['cache_hit']
    assert len(calls) == 4
    target = pricing.CACHE / (cache_key(*identity(a), 'changed evaluator') + '.json')
    broken = json.loads(target.read_text()); broken['data_qubits'] = D[::-1]
    target.write_text(json.dumps(broken))
    with pytest.raises(ValueError, match='cache identity mismatch'):
        price(a)


def test_cache_concurrent_same_key(tmp_path, monkeypatch):
    import multiprocessing
    import qtools.pricing as pricing
    monkeypatch.setattr(pricing, 'CACHE', tmp_path / 'prices')
    counter = tmp_path / 'calculations'
    def calculate(qasm, data, processes):
        with counter.open('a') as stream:
            stream.write('evaluated\n')
        return dict(loss=.001, acceptance=.6, width=1, basis={})
    monkeypatch.setattr(pricing, '_calculate', calculate)
    stem = write_stem('shared cache input', D, tmp_path, 'concurrent')
    with ProcessPoolExecutor(max_workers=2, mp_context=multiprocessing.get_context('fork')) as pool:
        results = list(pool.map(_price, [stem] * 8))
    assert counter.read_text().splitlines() == ['evaluated']
    assert sum(not r['cache_hit'] for r in results) == 1


def test_policy():
    assert expected_key_delta(3e-5, 3.1e-5, 2, 1) == pytest.approx(1e-6 - 1.1e-7)
    assert expected_key_delta(3e-5, 3e-5, 1, 2) == 1.1e-7
    old = dict(loss=3.7e-5, judge=dict(seconds=5., shots=10**6, processes=1, host='test'))
    new = dict(loss=3.6e-5, acceptance=.5002, raw={'ok': True},
               judge=dict(seconds=5., shots=10**6, processes=1, gates_ok=True, host='test'))
    assert is_finalist(new, old)
    for field, value in [('loss', old['loss']), ('acceptance', .5001999)]:
        bad = copy.deepcopy(new); bad[field] = value
        assert not is_finalist(bad, old)
    for field, value in [('seconds', 20.01), ('gates_ok', False), ('processes', 2),
                         ('shots', 100), ('host', 'another')]:
        bad = copy.deepcopy(new); bad['judge'][field] = value
        assert not is_finalist(bad, old)
    bad = copy.deepcopy(new); bad['raw']['ok'] = False
    assert not is_finalist(bad, old)
    bad = copy.deepcopy(new); bad['loss'] = old['loss'] - 1e-8; bad['judge']['seconds'] = 10
    assert not is_finalist(bad, old)


@pytest.mark.parametrize('name,loss,acceptance', [
    ('v37h', 3.611954991494179e-5, .5015489333258328),
    ('v37i', 3.591182404095001e-5, .5003576309837844)])
def test_reference_price_and_cache(name, loss, acceptance):
    result = price(MAIN / name, 1, use_cache=False)
    assert abs(result['loss'] - loss) <= 1e-15
    assert abs(result['acceptance'] - acceptance) <= 1e-12
    # Independently executed MAIN evaluator with its original (cold) saved bases.
    controls = json.loads((TOOLS / 'evidence/benchmark_sunfish.json').read_text())['legacy']
    cold = next(r for r in controls if r['source'] == 'MAIN/sparse' and Path(r['stem']).name == name)
    assert abs(result['loss'] - cold['loss']) <= 1e-15
    assert abs(result['acceptance'] - cold['acceptance']) <= 1e-12
    assert result['raw']['ok'] and result['exact_acceptance_ok']
    assert result['evaluator_version'] == EVALUATOR_VERSION
    start = time.perf_counter()
    hit = price(MAIN / name, 1)
    elapsed = time.perf_counter() - start
    assert hit['cache_hit'] and hit['loss'] == result['loss'] and elapsed < .1


def test_raw_invalid_decoded_zero(tmp_path):
    text = (MAIN / 'v37h.qasm').read_text()
    # The six gates implement X on one output; ideal decoding corrects it.
    bad = text + '\nh q[6];\n' + 't q[6];\n' * 4 + 'h q[6];\n'
    raw = raw_check(bad, D)
    assert not raw['ok'] and min(raw['six_stabilizers']) < -.999999
    from qtools.evaluator import sparse_walsh as sw
    # prepare asserts decoded ideal loss ~0: demonstrate exactly the loophole being closed.
    _, eng, *_ = sw.prepare(None, True, text=bad, data_qubits=D)
    acceptance, numerators = eng.ntable(0, 0)
    assert abs(acceptance-1) < 1e-10 and abs(numerators[0]) < 1e-15
    stem = write_stem(bad, D, tmp_path, 'raw_invalid')
    with pytest.raises(InvalidCircuit):
        price(stem, 1)


def test_empty_fourier_support():
    from qtools.evaluator.sparse_walsh import contract_quotient
    import numpy as np
    values, peak = contract_quotient([], np.array([], dtype=np.uint32), 0, [])
    assert values.size == 0 and peak == 0


def test_frontend_fails_closed_on_unsupported_format():
    from qtools.evaluator.frontend import parse_current
    with pytest.raises(ValueError, match='one QASM statement'):
        parse_current('h q[0]; h q[1];')
    with pytest.raises(ValueError, match='register name'):
        parse_current('qreg other[36];')
    ops, detectors = parse_current('  h q[0]; // comment\n  //   DETECTOR c[1]\n')
    assert len(ops) == 1 and ops[0].qs == (0,) and detectors == [{1}]
