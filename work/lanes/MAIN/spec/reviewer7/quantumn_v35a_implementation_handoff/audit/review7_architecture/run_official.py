"""Run the unmodified pinned official judge on the review-7 candidate.

No remote compute or submission. Dependencies live in this directory's venv.
The official check() function is called unchanged, including class diagnosis,
exact correctness, the noiseless cross-engine check, and the noisy sampler.
"""
from pathlib import Path
import dataclasses
import hashlib
import importlib.metadata
import importlib
import json
import resource
import sys
import time
import threading
import traceback

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "audit/review6_validation/official"))
import tprep
from tprep.qasm import to_stim
from tprep.noise import schedule


def main():
    target = json.loads((HERE / "target.json").read_text())
    if len(sys.argv) > 3:
        qasm_path = (ROOT / sys.argv[3]).with_suffix('.qasm')
        meta = json.loads(qasm_path.with_suffix('.json').read_text())
        target = dict(qasm=str(qasm_path.relative_to(ROOT)), data_qubits=meta['data_qubits'],
                      qasm_sha256=hashlib.sha256(qasm_path.read_bytes()).hexdigest(),
                      requested_shots=1000000, requested_seed=0)
        if len(sys.argv) > 4:
            assert target['qasm_sha256'] == sys.argv[4]
    qasm_path = ROOT / target["qasm"]
    raw = qasm_path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == target["qasm_sha256"]
    shots = int(sys.argv[1]) if len(sys.argv) > 1 else target["requested_shots"]
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else target["requested_seed"]
    target['requested_shots'], target['requested_seed'] = shots, seed
    name = qasm_path.stem
    stem = f"{name}.official_{shots}_{seed}"
    (HERE / f"{name}.qasm").write_bytes(raw)
    versions = {p: importlib.metadata.version(p) for p in ["xtim", "stim", "qiskit", "numpy", "scipy"]}
    result = dict(target=target, official_commit="76fe47c0324f1c1f8b72a7d55af200e88043b522",
                  versions=versions, shots=shots, seed=seed, tprep_version=tprep.__version__)
    print(json.dumps(result), flush=True)
    start = time.perf_counter()
    native, errors = to_stim(raw.decode())
    result["parser_seconds"] = time.perf_counter() - start
    result["parser_errors"] = errors
    if native is not None:
        (HERE / f"{name}.native.stim").write_text(native)
        prog, steps, gaps = schedule(native)
        result["native_instruction_counts"] = {k: sum(i.name == k for i in prog) for k in sorted({i.name for i in prog})}
        result["native_depth"] = max(t for group in steps for _, t in group) + 1
    print("Official OpenQASM conversion finished", json.dumps({k:v for k,v in result.items() if k.startswith("native_") or k.startswith("parser_")}), flush=True)
    stages = []
    replacements = []
    active = dict(stage='before official check', started=time.perf_counter())
    def timed(module, attr):
        original = getattr(module, attr)
        def call(*args, **kwargs):
            stage = attr + (f"({args[1]} shots)" if attr == '_sample' else '')
            print('START ' + stage, flush=True)
            t = time.perf_counter()
            active.update(stage=stage, started=t)
            try:
                return original(*args, **kwargs)
            finally:
                seconds = time.perf_counter() - t
                stages.append(dict(stage=stage, seconds=seconds))
                print('END ' + stage + ' ' + str(seconds), flush=True)
                active.update(stage='between official stages', started=time.perf_counter())
        setattr(module, attr, call)
        replacements.append((module, attr, original))
    import xtim
    check_module = importlib.import_module('tprep.check')
    exact_module = importlib.import_module('tprep.exact')
    for module, attr in [(xtim, 'diagnose'), (check_module, 'auto_frame'),
                         (exact_module, 'verify'), (check_module, '_sample')]:
        timed(module, attr)
    start = time.perf_counter()
    cpu_start = time.process_time()
    done = threading.Event()
    def heartbeat():
        while not done.wait(30):
            progress = dict(stage=active['stage'], elapsed_seconds=time.perf_counter()-start,
                            stage_seconds=time.perf_counter()-active['started'],
                            cpu_seconds=time.process_time()-cpu_start, finished=False)
            (HERE / (stem + '.progress.json')).write_text(json.dumps(progress, indent=2) + '\n')
            print('PROGRESS ' + json.dumps(progress), flush=True)
    monitor = threading.Thread(target=heartbeat, daemon=True)
    monitor.start()
    try:
        report = tprep.check(raw.decode(), target["data_qubits"], shots=shots, seed=seed)
        result["check_seconds"] = time.perf_counter() - start
        result["report"] = dataclasses.asdict(report)
        result["gates"] = {k: getattr(report, k) for k in ["format_ok", "class_ok", "correct_ok", "acceptance_ok", "passed"]}
        result["text_report"] = str(report)
        print(report, flush=True)
    except Exception:
        result["check_seconds"] = time.perf_counter() - start
        result["exception"] = traceback.format_exc()
        print(result["exception"], flush=True)
    finally:
        done.set()
        for module, attr, original in replacements:
            setattr(module, attr, original)
    result['check_cpu_seconds'] = time.process_time() - cpu_start
    result['stages'] = stages
    result["peak_rss_kib"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    (HERE / (stem + ".json")).write_text(json.dumps(result, indent=2, default=str) + "\n")
    (HERE / (stem + '.progress.json')).write_text(json.dumps(dict(finished=True, check_seconds=result['check_seconds'],
        gates=result.get('gates'), exception=result.get('exception')), indent=2) + '\n')
    print(json.dumps({k:v for k,v in result.items() if k in ["check_seconds", "peak_rss_kib", "gates"]}), flush=True)


if __name__ == "__main__":
    main()
