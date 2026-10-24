#!/usr/bin/env python3
"""Reuse a certified identity-detector basis in the sparse all-orders evaluator.

This changes evaluation coordinates only, never the physical circuit. It reads
an existing evaluator without modifying it and accepts a saved row-XOR proposal
only when every participating reduced projector is exactly identity with zero
reference. An invertible coordinate change preserves every accepted moment.
Nearby circuits may reuse the proposal; an inapplicable or costlier proposal
falls back to the original basis. No new basis search is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import multiprocessing as mp
from pathlib import Path
import sys
import time


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binary_rank(rows: list[int]) -> int:
    pivots: dict[int, int] = {}
    for row in rows:
        while row:
            lead = row.bit_length() - 1
            if lead not in pivots:
                pivots[lead] = row
                break
            row ^= pivots[lead]
    return len(pivots)


def transform_signature(signature: int, rows: list[int]) -> int:
    if signature < 0 or signature >> len(rows):
        raise ValueError('Fault signature exceeds the declared detector space')
    return sum(((signature & row).bit_count() & 1) << i
               for i, row in enumerate(rows))


def propose_basis(sw, model, engine, groups, nd, kernel_scope, certificate):
    """Return an independently checked compiled proposal and its proof metadata."""
    operations = certificate.get('elementary_row_xors')
    if not isinstance(operations, list):
        raise ValueError('Certificate must contain an elementary_row_xors list')
    for pair in operations:
        if (not isinstance(pair, list) or len(pair) != 2
                or any(type(x) is not int or x < 0 for x in pair)
                or pair[0] == pair[1]):
            raise ValueError(f'Invalid elementary row XOR: {pair!r}')
    proof = {
        'coordinate_origin': 'after sparse_walsh.prepare(stem, canonicalize=True)',
        'proposed_row_xors': operations,
        'proposed_operation_count': len(operations),
        'applicable': False,
    }
    referenced = sorted({i for pair in operations for i in pair})
    if any(i >= nd for i in referenced):
        proof['reason'] = 'Saved proposal refers to a detector absent in this candidate'
        return None, proof
    nonidentity = [i for i in referenced if engine.projs[i] != (0, 0, 1)]
    nonzero_reference = [i for i in referenced if int(engine.v[i]) != 0]
    active = sorted(i for i in kernel_scope if i < nd)
    if nonidentity or nonzero_reference or set(referenced) & set(active):
        proof['reason'] = 'Saved proposal touches a non-identity, nonzero-reference, or active detector'
        proof['nonidentity_rows'] = nonidentity
        proof['nonzero_reference_rows'] = nonzero_reference
        return None, proof
    # Each update is an invertible elementary operation; explicitly verify the
    # resulting matrix and ensure that the ideal-kernel coordinates are fixed.
    rows = [1 << i for i in range(nd)]
    for target, source in operations:
        assert engine.projs[target] == engine.projs[source] == (0, 0, 1)
        assert int(engine.v[target]) == int(engine.v[source]) == 0
        rows[target] ^= rows[source]
    rank = binary_rank(rows)
    if rank != nd or any(rows[i] != 1 << i for i in active):
        raise ValueError('Basis proposal failed its invertibility or kernel-preservation check')
    # compile_channels reads the transformed group dictionaries and original
    # channel probabilities. Neither the original model nor its groups change.
    transformed = {
        channel: [dict(fault, d=transform_signature(fault['d'], rows)) for fault in faults]
        for channel, faults in groups.items()
    }
    compiled = sw.compile_channels(model, transformed, nd, kernel_scope)
    proof.update(applicable=True, basis_rank=rank, detector_count=nd,
                 active_kernel_detectors=active,
                 transform_rows_hex=[hex(row) for row in rows],
                 checked_identity_rows=referenced,
                 reason='Invertible zero-reference identity-detector transformation')
    return compiled, proof


def evaluate(args):
    start = time.perf_counter()
    evaluator_dir = args.evaluator_dir.resolve()
    stem = args.stem.resolve()
    if stem.suffix in ('.qasm', '.json'):
        stem = stem.with_suffix('')
    certificate_path = args.certificate.resolve()
    certificate = json.loads(certificate_path.read_text())
    sys.path.insert(0, str(evaluator_dir))
    sw = importlib.import_module('sparse_walsh')
    if Path(sw.__file__).resolve().parent != evaluator_dir:
        raise ValueError('A different sparse_walsh module was already imported')
    model, engine, groups, nd, ks, psi, where, dense = sw.prepare(stem, True)
    keys = [None] + engine.keys
    if len(keys) != 73:
        raise ValueError(f'Expected acceptance plus 72 observables, found {len(keys)} moments')
    original = sw.compile_channels(model, groups, nd, ks)
    original_plan = sw.minfill([set(scope) for scope, _, _ in original])
    proposed, proof = propose_basis(sw, model, engine, groups, nd, ks, certificate)
    proposed_plan = None
    selected, selected_plan, selection = original, original_plan, 'original'
    if proposed is not None:
        proposed_plan = sw.minfill([set(scope) for scope, _, _ in proposed])
        old_cost = (original_plan['work_entries'], original_plan['width'])
        new_cost = (proposed_plan['work_entries'], proposed_plan['width'])
        if new_cost < old_cost:
            selected, selected_plan, selection = proposed, proposed_plan, 'saved_basis'
            proof['selection_reason'] = 'Strictly smaller min-fill (work_entries, width) tuple'
        else:
            proof['selection_reason'] = 'Fallback: saved proposal does not reduce the min-fill cost tuple'
    else:
        proof['selection_reason'] = 'Fallback: proposal is semantically inapplicable'
    planning_seconds = time.perf_counter() - start
    sw._CTX.update(eng=engine, ks=ks, psi=psi, where=where,
                   compiled=selected, elim=selected_plan)
    contraction_start = time.perf_counter()
    if args.processes == 1:
        results = [sw._row(key) for key in keys]
    else:
        if 'fork' not in mp.get_all_start_methods():
            raise ValueError('This evaluator requires POSIX fork for --processes > 1; use --processes 1')
        with mp.get_context('fork').Pool(args.processes) as pool:
            results = list(pool.imap(sw._row, keys))
    contraction_seconds = time.perf_counter() - contraction_start
    acceptance = results[0]['value']
    observable = sum(float(w * b) * row['value']
                     for w, b, row in zip(engine.W, engine.beta, results[1:]))
    e_acceptance = results[0]['absolute_kernel_omission_bound']
    e_observable = sum(abs(float(w * b)) * row['absolute_kernel_omission_bound']
                       for w, b, row in zip(engine.W, engine.beta, results[1:]))
    if acceptance <= e_acceptance:
        raise ValueError('Acceptance is not above its kernel-omission bound')
    loss = (acceptance - observable) / (2 * acceptance)
    omission = (e_observable / (2 * (acceptance - e_acceptance))
                + abs(observable) * e_acceptance
                / (2 * acceptance * (acceptance - e_acceptance)))
    sources = {name: sha256(evaluator_dir / name)
               for name in ('sparse_walsh.py', 'frontend.py')}
    out = {
        'source': str(stem),
        'source_qasm_sha256': sha256(stem.with_suffix('.qasm')),
        'source_json_sha256': sha256(stem.with_suffix('.json')),
        'evaluator_dir': str(evaluator_dir), 'evaluator_source_sha256': sources,
        'certificate_path': str(certificate_path),
        'certificate_sha256': sha256(certificate_path),
        'method': 'Sparse all-orders contraction with validated reusable identity-detector coordinates',
        'scope': 'Computation only; submitted circuit, channel probabilities, and physical loss are unchanged',
        'basis_selection': selection, 'basis_proof': proof,
        'original_plan': original_plan, 'proposed_plan': proposed_plan,
        'channels': len(model.chans), 'detectors': nd, 'kernel_bits': len(ks),
        'dense_width': dense['width'], 'conditioned_width': selected_plan['width'],
        'conditioned_work_entries': selected_plan['work_entries'],
        'max_peak_bucket_elements': max(row['peak_bucket_elements'] for row in results),
        'processes': args.processes, 'moments': len(results), 'results': results,
        'acceptance': acceptance, 'loss': loss,
        'conditional_loss_kernel_omission_bound': omission,
        'omission_bound_note': 'Sparse kernel cutoff only; excludes floating-point roundoff',
        'planning_seconds': planning_seconds,
        'contraction_seconds': contraction_seconds,
        'seconds': time.perf_counter() - start,
        'performance_note': 'Min-fill cost is a work proxy, not a wall-time guarantee; benchmark end-to-end on the target workload',
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=2) + '\n')
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evaluator-dir', type=Path, required=True)
    parser.add_argument('--stem', type=Path, required=True,
                        help='Candidate path with or without .qasm/.json suffix')
    parser.add_argument('--certificate', type=Path,
                        default=Path(__file__).resolve().with_name('basis_width_probe.json'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--processes', type=int, default=4)
    args = parser.parse_args()
    if args.processes < 1:
        parser.error('--processes must be positive')
    out = evaluate(args)
    print(json.dumps({key: out[key] for key in (
        'source_qasm_sha256', 'certificate_sha256', 'basis_selection',
        'channels', 'detectors', 'moments', 'conditioned_width',
        'conditioned_work_entries', 'max_peak_bucket_elements',
        'acceptance', 'loss', 'conditional_loss_kernel_omission_bound',
        'planning_seconds', 'contraction_seconds', 'seconds')}, indent=2))


if __name__ == '__main__':
    main()
