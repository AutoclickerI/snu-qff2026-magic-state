#!/usr/bin/env python3
"""Finite, reproducible rank-six phase-polynomial audit; Python standard library only.

Usage: python rank6_phase_audit.py [--output result.json] [--witness-only]
Default output is rank6_phase_certificate.json beside this script.

This verifies an algebraic phase representation and a PHASE-AXIS-ONLY fault
model. It is not a routed QASM circuit, a whole-circuit noise calculation,
xtim class validation, or an official score improvement.
"""
from __future__ import annotations
import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path
import time

PIN = 'f4b685ff12aed683def0697d42a6a48348efe48d'
SOURCE = ('https://github.com/AutoclickerI/quantumn/blob/' + PIN +
          '/work/lanes/MAIN/spec/reviewer9/quantumn_v36c_handoff/'
          'audit/review10/physical/phase_family_certificate.json')
N = 6
TARGET = 31
BASE = [1, 2, 4, 8, 7, 14, 13, 11, 16, 26, 22, 28, 21, 19, 25]
SUPPORT22 = [5, 6, 7, 9, 10, 11, 12, 17, 18, 19, 20, 24, 29, 30,
             35, 39, 43, 47, 51, 55, 59, 63]
NEGATIVE22 = {7, 11, 19}


def parity(v: int) -> int:
    return v.bit_count() & 1


def gf2_rank(vectors) -> int:
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length() - 1
            if bit in pivots:
                value ^= pivots[bit]
            else:
                pivots[bit] = value
                break
    return len(pivots)


def monomial_word(subset) -> int:
    return sum(1 << x for x in range(1, 64)
               if all((x >> j) & 1 for j in subset))


def rank_certificate():
    # Degree <=3 signatures determine a diagonal phase modulo diagonal Cliffords.
    signature = [monomial_word(subset) for degree in (1, 2, 3)
                 for subset in combinations(range(N), degree)]
    monomials = [()] + [(j,) for j in range(N)] + list(combinations(range(N), 2))
    kernel = [monomial_word(subset) for subset in monomials]
    base_word = sum(1 << x for x in BASE)
    result = {
        'axes': 63,
        'signature_rank': gf2_rank(signature),
        'kernel_dimension': gf2_rank(kernel),
        'all_kernel_generators_orthogonal': all(
            parity(a & b) == 0 for a in kernel for b in signature),
        'base_and_target_signatures_equal': all(
            parity((base_word ^ (1 << TARGET)) & b) == 0 for b in signature),
    }
    assert result['signature_rank'] == 41
    assert result['kernel_dimension'] == 22
    assert result['all_kernel_generators_orthogonal']
    assert result['base_and_target_signatures_equal']
    # 41 + 22 == 63 proves that these independent kernel generators are complete.
    result['complete_kernel_dimension_check'] = 41 + 22 == 63
    return kernel, result


def enumerate_supports(kernel):
    started = time.monotonic()
    reverse16 = [int(f'{x:016b}'[::-1], 2) for x in range(65536)]

    def translate_target(word):
        # Axis x -> x XOR 31: reverse the 32 bits within each half.
        return ((reverse16[word & 65535] << 16)
                | reverse16[(word >> 16) & 65535]
                | (reverse16[(word >> 32) & 65535] << 48)
                | (reverse16[(word >> 48) & 65535] << 32))

    word = sum(1 << x for x in BASE)
    under20 = Counter()
    target_absent_hist = Counter()
    min_rank6 = 64
    min_protected = 64
    minimum_count = protected_count = 0
    min_examples = []
    protected_examples = []
    for index in range(1 << 22):
        if index:
            # Consecutive Gray words differ in the least significant set bit of index.
            word ^= kernel[(index & -index).bit_length() - 1]
        if (word >> TARGET) & 1:
            continue
        size = word.bit_count()
        target_absent_hist[size] += 1
        if size > min_rank6 and size > min_protected:
            continue
        bad_pairs = (word & translate_target(word)).bit_count() // 2
        if size > min_rank6 and bad_pairs:
            continue
        support = [x for x in range(1, 64) if (word >> x) & 1]
        rank = gf2_rank(support)
        if size <= 20:
            under20[(size, rank, bad_pairs)] += 1
        if rank != 6:
            continue
        example = {'T_odd_support': size, 'coordinate_rank': rank,
                   'target_xor_pairs': bad_pairs, 'support': support}
        if size < min_rank6:
            min_rank6 = size
            minimum_count = 0
            min_examples = []
        if size == min_rank6:
            minimum_count += 1
            if len(min_examples) < 3:
                min_examples.append(example)
        if bad_pairs == 0:
            if size < min_protected:
                min_protected = size
                protected_count = 0
                protected_examples = []
            if size == min_protected:
                protected_count += 1
                if len(protected_examples) < 2:
                    protected_examples.append(example)
    assert under20 == Counter({(15, 5, 0): 496, (14, 4, 7): 155})
    assert min_rank6 == 22 and minimum_count == 39928
    assert min_protected == 31 and protected_count == 32768
    return {
        'enumerated_odd_supports': 1 << 22,
        'target_absent_support_histogram': dict(sorted(target_absent_hist.items())),
        'at_most20_T_without_target_axis': [
            {'T_odd_support': t, 'coordinate_rank': r,
             'target_xor_pairs': b, 'count': count}
            for (t, r, b), count in sorted(under20.items())],
        'minimum_genuine_rank6_T_without_target_axis': min_rank6,
        'number_of_minimum_supports': minimum_count,
        'minimum_support_examples': min_examples,
        'minimum_genuine_rank6_T_without_target_axis_or_target_xor_pairs': min_protected,
        'number_of_minimum_pair_protected_supports': protected_count,
        'pair_protected_examples': protected_examples,
        'elapsed_seconds': time.monotonic() - started,
    }


def verify_witness():
    coefficients = [-1 if axis in NEGATIVE22 else 1 for axis in SUPPORT22]
    differences = [
        (sum(c * parity(axis & y) for axis, c in zip(SUPPORT22, coefficients))
         - parity(TARGET & y)) % 8 for y in range(64)]
    assert differences == [0] * 64
    assert gf2_rank(SUPPORT22) == 6
    bad_pairs = [[a, b] for a, b in combinations(SUPPORT22, 2) if a ^ b == TARGET]
    assert bad_pairs == [[7, 24], [11, 20], [12, 19]]
    # Idealized old detector map accepts axes 0 and31. The sixth coordinate is
    # an additional perfect flag: a phase-axis error with bit5 set is rejected.
    q = Fraction(1, 3000)  # only the p/3 commuting phase component of T noise
    distribution = [Fraction(0) for _ in range(64)]
    distribution[0] = Fraction(1)
    for axis in SUPPORT22:
        distribution = [(1 - q) * distribution[y] + q * distribution[y ^ axis]
                        for y in range(64)]
    acceptance = distribution[0] + distribution[TARGET]
    numerator = distribution[TARGET]
    loss = numerator / acceptance
    return {
        'support': SUPPORT22,
        'coefficients': coefficients,
        'coordinate_rank': 6,
        'all64_mod8_phase_equalities_passed': True,
        'residual_Clifford_correction_needed': False,
        'target_axis_absent': TARGET not in SUPPORT22,
        'target_xor_pairs': bad_pairs,
        'phase_axis_only_q': str(q),
        'phase_axis_only_acceptance': float(acceptance),
        'phase_axis_only_loss': float(loss),
        'phase_axis_only_acceptance_exact': str(acceptance),
        'phase_axis_only_loss_exact': str(loss),
        'expected_leading_phase_loss': '3*(p/3)^2 = p^2/3; not a full-noise coefficient',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=Path(__file__).resolve().with_name('rank6_phase_certificate.json'))
    parser.add_argument('--witness-only', action='store_true')
    args = parser.parse_args()
    kernel, certificate = rank_certificate()
    report = {
        'repository_commit': PIN,
        'source_for_base_phase_and_fault_map': SOURCE,
        'scope': [
            'Commuting phase-polynomial odd supports over six independent binary coordinates.',
            'One target linear parity, axis31; equivalence modulo diagonal Clifford corrections.',
            'MinimumT claims count distinct odd-support rotations; not arbitrary measured quantum circuits.',
            'The explicit22T witness has exact phase equality, requiring no Clifford correction.',
            'Only p/3 phase-axis faults are modeled; all other channels and exterior faults are perfect.',
            'No grid routing, native schedule, whole-circuit acceptance/loss, or xtim runtime was verified.',
        ],
        'signature_certificate': certificate,
        'witness22': verify_witness(),
    }
    if not args.witness_only:
        report['exhaustive_enumeration'] = enumerate_supports(kernel)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'output': str(args.output),
                      'witness_phase_loss': report['witness22']['phase_axis_only_loss'],
                      'exhaustive': not args.witness_only}, indent=2))

if __name__ == '__main__':
    main()
