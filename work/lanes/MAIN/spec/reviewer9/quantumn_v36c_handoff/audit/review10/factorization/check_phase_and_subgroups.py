#!/usr/bin/env python3
"""Portable finite-algebra checker; Python standard library only.

Checks the supplied phase certificates internally, without importing an
evaluator, Qiskit, Stim, or NumPy. It does not independently derive the
phase/response extraction from a quantum circuit. The 14-T noise calculation
is the explicitly relaxed phase-axis-only model, not full physical loss.

Example from this directory:
    python3 check_phase_and_subgroups.py --phase-dir ../physical
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations
import json
import math
from pathlib import Path
import time


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rank(rows):
    pivots = {}
    for row in rows:
        while row:
            p = row.bit_length() - 1
            if p not in pivots:
                pivots[p] = row
                break
            row ^= pivots[p]
    return len(pivots)


def span(rows):
    values = {0}
    for row in rows:
        values |= {x ^ row for x in tuple(values)}
    return values


def parity(x):
    return x.bit_count() & 1


def xor_distribution(support, q, dimension=5):
    """Exact convolution of independent Bernoulli axis faults on F_2^n."""
    dist = [Fraction(0) for _ in range(1 << dimension)]
    dist[0] = Fraction(1)
    for axis in support:
        dist = [(1-q)*dist[x] + q*dist[x ^ axis]
                for x in range(1 << dimension)]
    require(sum(dist) == 1, 'XOR distribution is not normalized')
    require(all(x >= 0 for x in dist), 'Negative XOR probability')
    return dist


def monomial(mask, assignment):
    return int((mask & assignment) == mask)


def phase_values(support, coefficients, residual=(), dimension=5):
    return [
        (sum(c * parity(axis & y) for axis, c in zip(support, coefficients))
         + sum(term['phase_mod8'] * monomial(term['monomial_mask'], y)
               for term in residual)) % 8
        for y in range(1 << dimension)
    ]


def zero_residual_sign_count(support, target_values):
    """Count +/- sign assignments with no residual Clifford using a Gray walk.

    A representative with zero residual already proves the nonnegative term
    count minimum is zero. This extra finite enumeration checks the reported
    number of minimizers, without reusing the certificate generator's arrays.
    """
    columns = [[parity(axis & y) for y in range(len(target_values))]
               for axis in support]
    values = [sum(column[y] for column in columns) % 8
              for y in range(len(target_values))]
    count = int(values == target_values)
    old_gray = 0
    for index in range(1, 1 << len(support)):
        gray = index ^ (index >> 1)
        changed = gray ^ old_gray
        j = changed.bit_length() - 1
        delta = -2 if gray & changed else 2
        values = [(value + delta*column) % 8
                  for value, column in zip(values, columns[j])]
        count += values == target_values
        old_gray = gray
    return count


def enumerate_subspaces(n):
    """Exactly one reduced-row-echelon basis for each subspace of F_2^n.

    Columns are numbered from bit 0. Every pivot column has one 1, every row
    is zero before its pivot, and only nonpivot entries after a pivot are free.
    """
    for dimension in range(n + 1):
        for pivots in combinations(range(n), dimension):
            nonpivots = set(range(n)) - set(pivots)
            free = [(i, j) for i, p in enumerate(pivots)
                    for j in sorted(nonpivots) if j > p]
            for assignment in range(1 << len(free)):
                rows = [1 << p for p in pivots]
                for b, (i, j) in enumerate(free):
                    rows[i] |= ((assignment >> b) & 1) << j
                yield dimension, tuple(rows)


def gaussian_binomial(n, k):
    value = Fraction(1)
    for j in range(k):
        value *= Fraction((1 << (n-j))-1, (1 << (k-j))-1)
    require(value.denominator == 1, 'Nonintegral Gaussian binomial')
    return int(value)


def check_phase(phase_dir):
    family_path = phase_dir / 'phase_family_certificate.json'
    signs_path = phase_dir / 'phase_sign_certificate.json'
    family = json.loads(family_path.read_text())
    signs = json.loads(signs_path.read_text())
    require(family['rank'] == 5, 'Expected the supplied rank-five phase space')
    dimension = 5
    states = 1 << dimension
    target = family['target_axis']
    require(0 < target < states, 'Invalid target axis')
    base_support = [x['coordinate'] for x in family['base_axes']]
    base_coefficients = [x['coefficient'] for x in family['base_axes']]
    require(len(set(base_support)) == 15, 'Base support does not contain 15 axes')
    require(rank(base_support) == 5, 'Base support rank is not five')
    base_phase = phase_values(base_support, base_coefficients)
    target_phase = [parity(target & y) for y in range(states)]
    require(base_phase == target_phase, 'Base phase does not equal target parity')
    response = family['response']
    require([r['axis'] for r in response] == list(range(states)), 'Response axes reordered')
    # The response extraction is input evidence. Check the exact binary pattern
    # needed by the subsequent, independently recomputed rational calculation.
    require(all(abs(r['A']-int(r['axis'] in (0, target))) < 1e-12
                for r in response), 'Unexpected acceptance response')
    require(all(abs(r['N']-int(r['axis'] == target)) < 1e-12
                for r in response), 'Unexpected loss-numerator response')
    for y in range(states):
        expected_d = expected_e = 0
        for bit in range(dimension):
            if y >> bit & 1:
                expected_d ^= int(response[1 << bit]['detector_signature'])
                expected_e ^= response[1 << bit]['output_signature']
        require(expected_d == int(response[y]['detector_signature']), 'Nonlinear detector signature')
        require(expected_e == response[y]['output_signature'], 'Nonlinear output signature')
    p = Fraction(str(family['p']))
    q = p / 3
    require(q == Fraction(1, 3000), 'Expected p=1/1000 and q=p/3')
    require(abs(family['phase_axis_probability']-float(q)) < 1e-18, 'Incorrect axis probability')
    r = 1-2*q
    formula_a = (1+7*r**8)/8
    formula_n = (1+7*r**8-8*r**7)/16
    formula_l = formula_n/formula_a
    formulas = family['fourteen_T_formula']
    for key, value in [('A_at_p001', formula_a), ('N_at_p001', formula_n), ('L_at_p001', formula_l)]:
        require(Fraction(formulas[key]) == value, f'Incorrect rational formula field {key}')
    require(math.isclose(formulas['L_float'], float(formula_l), rel_tol=1e-12), 'Incorrect formula float')
    rows = family['forms']
    by_id = {row['id']: row for row in rows}
    require(len(by_id) == len(rows) == 64, 'Expected 64 distinct family members')
    expected_ids = {f'f{a:02d}_{c}' for a in range(32) for c in range(2)}
    require(set(by_id) == expected_ids, 'Incorrect family IDs')
    checked = []
    for a in range(32):
        for c in range(2):
            row = by_id[f'f{a:02d}_{c}']
            support = sorted(set(base_support) ^ {
                x for x in range(1, states) if parity(a & x) ^ c})
            require(row['support'] == support, f'{row["id"]}: incorrect affine-family support')
            require(row['T'] == len(support), f'{row["id"]}: wrong T count')
            actual_rank = rank(support)
            require(row['phase_coordinate_rank'] == actual_rank, f'{row["id"]}: wrong rank')
            bad_singles = [x for x in support if x == target]
            bad_pairs = [list(pair) for pair in combinations(support, 2)
                         if pair[0] ^ pair[1] == target]
            require(row['bad_singles'] == bad_singles, f'{row["id"]}: bad singles differ')
            require(row['bad_pairs'] == bad_pairs, f'{row["id"]}: bad pairs differ')
            dist = xor_distribution(support, q)
            accept = dist[0] + dist[target]
            numerator = dist[target]
            loss = numerator / accept
            for key, value in [('A', accept), ('N', numerator), ('L', loss)]:
                require(math.isclose(row[key], float(value), rel_tol=2e-12, abs_tol=2e-15),
                        f'{row["id"]}: {key} does not match exact convolution')
            if len(support) == 14:
                require(actual_rank == 4, 'A 14-T support has rank other than four')
                require(not bad_singles and len(bad_pairs) == 7, '14-T single/pair count differs')
                require(span(support) == set(support) | {0, target}, '14-T support is not a punctured four-space')
                require((accept, numerator, loss) == (formula_a, formula_n, formula_l), '14-T rational formula fails')
                require(phase_values(support, [1]*14, row['residual_clifford']) == base_phase,
                        'Unsigned 14-T support plus residual Clifford does not equal base phase')
            checked.append({'id':row['id'], 'T':len(support), 'rank':actual_rank,
                            'bad_single_count':len(bad_singles), 'bad_pair_count':len(bad_pairs),
                            'A_exact':str(accept), 'N_exact':str(numerator), 'L_exact':str(loss),
                            'xor_distribution_exact':[str(value) for value in dist]})
    expected_counts = {str(k):v for k,v in Counter(row['T'] for row in rows).items()}
    require(family['count_by_T'] == expected_counts, 'Family T-count histogram differs')
    sign_rows = signs['forms']
    fourteen_ids = {row['id'] for row in rows if row['T'] == 14}
    require(len(fourteen_ids) == 15, 'Expected fifteen 14-T supports')
    require({row['id'] for row in sign_rows} == fourteen_ids and len(sign_rows) == 15, 'Sign rows are incomplete')
    sign_results = []
    for row in sign_rows:
        support = row['support']
        require(support == by_id[row['id']]['support'], 'Signed support differs')
        require(len(row['T_coefficients']) == 14 and set(row['T_coefficients']) <= {-1, 1}, 'Invalid T signs')
        require(phase_values(support, row['T_coefficients'], row['residual_clifford']) == base_phase,
                f'{row["id"]}: signed phase differs on a basis assignment')
        require(row['residual_clifford'] == [] and row['minimum_virtual_clifford_terms'] == 0,
                'Expected the certified zero-residual witness')
        count = zero_residual_sign_count(support, base_phase)
        require(count == row['number_of_minimizers'] == 16, 'Zero-residual sign count differs')
        sign_results.append({'id':row['id'], 'assignments_checked':states,
                             'zero_residual_minimum':0, 'zero_residual_sign_solutions':count})
    return {
        'passed':True, 'source_hashes':{
            family_path.name:hashlib.sha256(family_path.read_bytes()).hexdigest(),
            signs_path.name:hashlib.sha256(signs_path.read_bytes()).hexdigest()},
        'scope':'Internal finite algebra only. Circuit-to-phase and circuit-to-response extraction remain supplied evidence. Phase-axis noise excludes other Pauli components, synthesis, Clifford corrections, preparations, measurements and idles.',
        'base_rank':5, 'target_axis':target, 'family_size':64,
        'fourteen_T_supports':15, 'fourteen_T_rank':4,
        'fourteen_T_bad_singles':0, 'fourteen_T_bad_pairs':7,
        'p':str(p), 'q':str(q), 'formula':{
            'r':'1-2*q','A':'(1+7*r**8)/8','N':'(1+7*r**8-8*r**7)/16',
            'A_exact':str(formula_a),'N_exact':str(formula_n),'L_exact':str(formula_l),
            'L_float':float(formula_l)},
        'family_checks':checked, 'sign_checks':sign_results,
    }


def check_subspaces():
    counts = [0]*7
    seen_spans = set()
    rows_out = []
    for dimension, rows in enumerate_subspaces(6):
        require(rank(rows) == dimension, 'Generated RREF basis has wrong rank')
        values = span(rows)
        require(len(values) == 1 << dimension, 'Generated subspace has wrong size')
        encoded = sum(1 << x for x in values)
        require(encoded not in seen_spans, 'Duplicate subspace generated')
        seen_spans.add(encoded)
        counts[dimension] += 1
        rows_out.append({'dimension':dimension, 'rref_rows':list(rows), 'span_bitset_hex':hex(encoded)})
    expected = [1,63,651,1395,651,63,1]
    require(counts == expected, 'Incorrect subspace counts')
    require(counts == [gaussian_binomial(6,k) for k in range(7)], 'Gaussian-binomial crosscheck fails')
    require(sum(counts) == len(seen_spans) == 2825, 'Incorrect total count')
    return {'passed':True, 'ambient_dimension':6, 'counts_by_dimension':counts,
            'total':2825, 'construction':'Unique RREF bases; distinct spans checked exhaustively; independent Gaussian-binomial crosscheck.',
            'scope':'This is an exhaustive family of linear subspaces of six syndrome bits, not a proof that each corresponding quantum measurement is useful or cheaply realizable.',
            'subspaces':rows_out}


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase-dir',type=Path,default=here.parent/'physical',
                        help='Directory containing both phase certificate JSONs; relative paths use the current working directory.')
    parser.add_argument('--output',type=Path,default=here/'phase_subgroup_verification.json')
    args = parser.parse_args()
    start = time.perf_counter()
    result = {'checker':'check_phase_and_subgroups.py', 'dependencies':'Python standard library only',
              'phase':check_phase(args.phase_dir), 'syndrome_subspaces':check_subspaces()}
    result['passed'] = True
    result['seconds'] = time.perf_counter()-start
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':True, 'fourteen_T_supports':result['phase']['fourteen_T_supports'],
                      'rank':4,'bad_singles_each':0,'bad_pairs_each':7,
                      'phase_axis_only_L':result['phase']['formula']['L_float'],
                      'signed_representatives_checked':len(result['phase']['sign_checks']),
                      'F2_6_counts':result['syndrome_subspaces']['counts_by_dimension'],
                      'F2_6_total':2825,'seconds':result['seconds'],'output':str(args.output)},indent=2))


if __name__ == '__main__':
    main()
