"""Exact Boolean-policy oracle from zero-reference detector relaxations.

Event mask S means every detector in S is zero and all unmentioned external
detectors are zero. The supplied masses must use the same unchanged circuit;
physically computing a new record adds noise that this oracle does not price.
"""
from fractions import Fraction
from pathlib import Path
import json


def coefficients(accept_by_syndrome):
    """Return c[S] with f(d)=sum_S c[S]*prod_{i in S} 1[d_i=0]."""
    size = len(accept_by_syndrome)
    if size == 0 or size & (size - 1):
        raise ValueError("Truth-table length must be a positive power of two")
    full = size - 1
    c = [int(accept_by_syndrome[full ^ u]) for u in range(size)]
    for bit in range(size.bit_length() - 1):
        for mask in range(size):
            if mask & (1 << bit):
                c[mask] -= c[mask ^ (1 << bit)]
    return c


def combine(accept_by_syndrome, acceptance_events, numerator_events):
    """Combine A and unnormalized N independently; never average losses."""
    c = coefficients(accept_by_syndrome)
    if len(c) != len(acceptance_events) or len(c) != len(numerator_events):
        raise ValueError("A complete, consistently indexed event table is required")
    A = sum(v * a for v, a in zip(c, acceptance_events))
    N = sum(v * n for v, n in zip(c, numerator_events))
    return {"coefficients": c, "acceptance": A, "numerator": N,
            "loss": N / A if A else None}


def certify():
    # Enumerate every Boolean predicate on three bits, using nonuniform exact
    # sector probabilities and distinct sector losses. No numerical tolerances.
    sectors_A = [Fraction(i + 1, 72) for i in range(8)]
    sectors_N = [a * Fraction((3*i + 2) % 11, 20000)
                 for i, a in enumerate(sectors_A)]
    events_A = [sum(a for d, a in enumerate(sectors_A) if not (d & s))
                for s in range(8)]
    events_N = [sum(n for d, n in enumerate(sectors_N) if not (d & s))
                for s in range(8)]
    for truth in range(256):
        policy = [(truth >> d) & 1 for d in range(8)]
        got = combine(policy, events_A, events_N)
        assert got["acceptance"] == sum(a*f for a, f in zip(sectors_A, policy))
        assert got["numerator"] == sum(n*f for n, f in zip(sectors_N, policy))
    assert coefficients([1, 1, 1, 0]) == [0, 1, 1, -1]
    return {"boolean_functions_checked": 256, "bits": 3,
            "arithmetic": "fractions.Fraction", "all_exact_equal": True,
            "NAND_coefficients_2bit": [0, 1, 1, -1],
            "scope": "Policy identity only. No gate noise, layout, or processability claim."}


if __name__ == "__main__":
    result = certify()
    Path(__file__).with_name("boolean_policy_certificate.json").write_text(
        json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
