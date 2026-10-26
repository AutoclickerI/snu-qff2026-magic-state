#!/usr/bin/env python3
"""Reproduce local exact expectations and ideal/single-fault checks; no submissions.

Use the pinned quantumn checkout's Python environment and --repo path.
This calls its evaluator in memory and never writes into the checkout.
"""
import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True

for name in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[name] = '1'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--circuit', type=Path, required=True, help='QASM path; companion JSON is required')
    ap.add_argument('--processes', type=int, default=1)
    ap.add_argument('--skip-singles', action='store_true')
    ap.add_argument('--out', type=Path)
    args = ap.parse_args()
    assert args.processes >= 1
    sp = args.repo.resolve() / 'work/lanes/MAIN/sparse'
    sys.path.insert(0, str(sp))
    import sparse_walsh as sw
    import frontend as fa

    stem = args.circuit.resolve().with_suffix('')
    started = time.perf_counter()
    with contextlib.redirect_stdout(io.StringIO()):
        model, engine, groups, nd, ks, psi, where, dense = sw.prepare(stem, True)
        state = engine.phi(0)
        for j, projector in enumerate(engine.projs):
            state = (state + (1 - 2 * int(engine.v[j])) * engine.apply(state, projector)) / 2
        norm = float((state.conj() * state).sum().real)
        raw_stabs = []
        for x, z, coefficient in model.gen_m:
            translated_x = engine.B.express(x)
            raw_stabs.append(0.0 if translated_x is None else engine.expect(
                state, (translated_x, engine._w(z), coefficient)) / norm)
        ideal_A, ideal_N = engine.ntable(0, 0)
        commuting_rotations = all(fa.comm(a[:3], b[:3]) == 0
                                 for i, a in enumerate(model.rots) for b in model.rots[i + 1:])
        assert all(abs(value - 1) < 1e-9 for value in raw_stabs), raw_stabs
        assert commuting_rotations, 'Pulled-back T axes do not commute'
        singles = None
        if not args.skip_singles:
            table = {}
            harmful = []
            total = 0.0
            for fault in model.faults:
                k = fault['s'], fault['d']
                if k not in table:
                    table[k] = engine.ntable(*k)
                probability, loss_vector = table[k]
                contribution = 0.0 if loss_vector is None else float(loss_vector[fault['e']])
                total += fault['p'] * contribution
                if contribution > 1e-9:
                    harmful.append(fault['label'])
            singles = {'atoms': len(model.faults), 'harmful_atoms_above_1e_9': len(harmful),
                       'first_order_contribution_at_p001': total / ideal_A,
                       'harmful_examples': harmful[:10]}
        compiled, elimination = sw.compile_best(model, engine, groups, nd, ks)
        sw._CTX.update(eng=engine, ks=ks, psi=psi, where=where, compiled=compiled, elim=elimination)
        keys = [None] + engine.keys
        if args.processes == 1:
            rows = [sw._row(k) for k in keys]
        else:
            import multiprocessing as mp
            with mp.get_context('fork').Pool(args.processes) as pool:
                rows = list(pool.imap(sw._row, keys))
    acceptance = rows[0]['value']
    observable = sum(w * b * row['value'] for w, b, row in zip(engine.W, engine.beta, rows[1:]))
    err_a = rows[0]['absolute_kernel_omission_bound']
    err_o = sum(abs(w * b) * row['absolute_kernel_omission_bound']
                for w, b, row in zip(engine.W, engine.beta, rows[1:]))
    bound = err_o / (2 * (acceptance - err_a)) + abs(observable) * err_a / (2 * acceptance * (acceptance - err_a))
    result = {
        'circuit': str(stem), 'qasm_sha256': hashlib.sha256(stem.with_suffix('.qasm').read_bytes()).hexdigest(),
        'ordered_data_qubits': json.loads(stem.with_suffix('.json').read_text())['data_qubits'],
        'loss': (acceptance - observable) / (2 * acceptance), 'acceptance': acceptance,
        'ideal_acceptance': ideal_A, 'ideal_decoded_loss': float(ideal_N[0] / ideal_A),
        'raw_output_stabilizers': raw_stabs, 'pulled_T_axes_commute': commuting_rotations,
        'single_fault_screen': singles, 'channels': len(model.chans), 'factors': len(compiled),
        'conditioned_width': elimination['width'], 'seconds': time.perf_counter() - started,
        'conditional_loss_kernel_omission_bound': bound,
        'bound_scope': 'Sparse coefficient cutoff only; excludes floating-point roundoff.',
        'official_xtim_judge_run': False,
        'evaluator_hashes': {f: hashlib.sha256((sp / f).read_bytes()).hexdigest()
                             for f in ('sparse_walsh.py', 'frontend.py', 'fastfill.py', 'basis_warm.json')},
    }
    output = json.dumps(result, indent=2, ensure_ascii=False) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(output)
    print(output, end='')


if __name__ == '__main__':
    main()
