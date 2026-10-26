"""Organizer raw correctness and the actual one-process, 1e6-shot judge."""
import importlib.util
import hashlib
import os
from pathlib import Path
import socket
import time
from .stems import read_stem, outputs
from .version import TOOLS


def raw_check(qasm_text, data_qubits):
    from tprep.qasm import to_stim
    from tprep.exact import verify, run, ExactError
    from tprep.grid import SUPPORTS
    data = outputs(data_qubits)
    stim, errors = to_stim(qasm_text)
    if errors:
        return {'ok': False, 'errors': errors, 'six_stabilizers': []}
    # Shared evaluator scope is zero frame / no postselection; never mischeck a declaration.
    import re
    if re.search(r'//\s*(FRAME_[XZ]|POSTSELECT)\b', qasm_text):
        raise ValueError('qtools supports zero-frame/no-POSTSELECT circuits only')
    try:
        result = verify(stim, data)
        state, inverse, _, _, wires = run(stim, 36)
        values = []
        for pauli in 'XZ':
            for support in SUPPORTS:
                observable = state.stim.PauliString(state.n)
                for i in support:
                    observable[wires[data[i]]] = pauli
                values.append(state.expectation(observable, inverse))
        result.pop('detector_values', None)
        result['six_stabilizers'] = values
        result['ok'] = not result['errors'] and all(abs(v - 1) <= 1e-9 for v in values)
        return result
    except ExactError as error:
        return {'ok': False, 'errors': [str(error)], 'six_stabilizers': []}


def judge_check(stem):
    """Time work/fast_check.check itself; imports and raw check are outside the draw timer."""
    import xtim
    xtim.cache_dir = str(TOOLS / 'cache' / 'xtim')
    os.environ['XTIM_TWIRL_CACHE_DIR'] = str(TOOLS / 'cache' / 'twirl')
    script = TOOLS.parent / 'fast_check.py'
    spec = importlib.util.spec_from_file_location('_qtools_fast_check', script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    qasm, data = read_stem(stem)
    start = time.perf_counter()
    report = module.check(qasm.decode(), list(data), shots=1_000_000, procs=1)
    seconds = time.perf_counter() - start
    return dict(gates_ok=bool(report.correct_ok), seconds=seconds, shots=1_000_000, processes=1,
                host=socket.gethostname(), measured_at=time.time(), load=os.getloadavg()[0],
                qasm_sha256=hashlib.sha256(qasm).hexdigest(), data_qubits=list(data),
                fast_check_sha256=hashlib.sha256(script.read_bytes()).hexdigest(),
                sampled_loss=report.score, sampled_acceptance=report.acceptance,
                format_errors=report.format_errors, class_error=report.class_error,
                correctness_errors=report.correctness_errors)


def validate(stem, processes=1):
    from .pricing import price
    result = price(stem, processes)
    result['judge'] = judge_check(stem)
    if any(result[k] != result['judge'][k] for k in ('qasm_sha256', 'data_qubits')):
        raise ValueError('stem changed between price and judge check')
    return result
