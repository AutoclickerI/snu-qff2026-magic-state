"""Exact, stdlib-only local phase certificate for the new A readout contract.

Run: python audit/review7_architecture/flag_conditioned_encoder_certificate.py
This certifies Pauli detection and reweights published EXENC local danger
vectors. It does not predict a complete noisy circuit's conditional loss.
"""

from fractions import Fraction
from itertools import combinations
import json
from pathlib import Path


COMMIT = "f843cb2a2a7e23e53cb2ba54b891d42943bfedfe"
BASE = f"https://github.com/AutoclickerI/quantumn/blob/{COMMIT}/"
CELLS = (1, 14, 8, 9, 2, 16, 15)
FLAG = frozenset((2, 3, 6))
Z_CHECKS = ((0, 2, 4, 6), (1, 2, 5, 6), (3, 4, 5, 6))


def mask(indices):
    return sum(1 << index for index in indices)


def span(generators):
    result = {0}
    for generator in generators:
        result |= {word ^ generator for word in tuple(result)}
    return result


def certify():
    flag = mask(FLAG)
    all_seven = (1 << 7) - 1
    stabilizers = span(tuple(map(mask, Z_CHECKS)))
    assert len(stabilizers) == 8
    assert all((flag & mask(check)).bit_count() % 2 == 0 for check in Z_CHECKS)
    assert flag not in stabilizers
    assert (flag ^ all_seven) in stabilizers

    pairs = []
    for i, j in combinations(range(7), 2):
        pair = (1 << i) ^ (1 << j)
        completion = ((i + 1) ^ (j + 1)) - 1
        # The Fano line {i,j,k} is a logical Z representative.
        assert pair ^ (1 << completion) ^ all_seven in stabilizers
        flag_flips = bool((flag & pair).bit_count() % 2)
        assert flag_flips == (completion not in FLAG)
        pairs.append({
            "code_indices": [i, j],
            "physical_cells": [CELLS[i], CELLS[j]],
            "old_Z_readout_detects_phase_component": False,
            "new_X_flag_flips": flag_flips,
            "equivalent_phase_class": f"Z_L Z_{completion}",
            "fano_line_completion": completion,
        })
    detected = sum(row["new_X_flag_flips"] for row in pairs)
    assert (len(pairs), detected, len(pairs) - detected) == (21, 12, 9)

    # Published vector order: pure logical Z, Z_L Z_0, ..., Z_L Z_6.
    # Values are exact multiples of p/15, not complete circuit loss.
    published = [
        ("reference", None, None, [0, 3, 3, 0, 4, 0, 0, 0], 10, 4),
        ("13_CX_ASAP_depth_7", 13, 7, [0, 0, 0, 0, 0, 4, 2, 3], 9, 3),
        ("13_CX_ASAP_depth_8", 13, 8, [0, 0, 0, 0, 3, 3, 0, 3], 9, 6),
        ("12_CX_ASAP_depth_9", 12, 9, [0, 5, 0, 0, 3, 0, 0, 0], 8, 3),
    ]
    class_detected = [True] + [index not in FLAG for index in range(7)]
    profiles = []
    for name, cx, depth, vector, expected_old, expected_blind in published:
        old = sum(vector)
        blind = sum(value for value, catches in zip(vector, class_detected) if not catches)
        assert (old, blind) == (expected_old, expected_blind)
        profiles.append({
            "published_profile": name,
            "CX": cx,
            "ASAP_depth": depth,
            "danger_vector_units_p_over_15": vector,
            "old_total_units": old,
            "new_flag_blind_units": blind,
            "new_flag_detected_units": old - blind,
            "old_local_danger_at_p_0_001_exact": str(Fraction(old, 15000)),
            "flag_blind_local_proxy_at_p_0_001_exact": str(Fraction(blind, 15000)),
        })

    return {
        "source_commit": COMMIT,
        "scope": "Exact local phase-detection certificate and published-vector reweighting; no encoder rerun or full-circuit performance claim.",
        "code_index_to_physical_cell": list(CELLS),
        "X_flag_code_support": sorted(FLAG),
        "X_flag_physical_support": [CELLS[index] for index in sorted(FLAG)],
        "Z_syndrome_supports": list(map(list, Z_CHECKS)),
        "flag_is_logical_X_mod_stabilizers": True,
        "pure_weight_two_Z_pairs": pairs,
        "pair_count": len(pairs),
        "detected_pairs": detected,
        "blind_pairs": len(pairs) - detected,
        "phase_class_order": ["Z_L"] + [f"Z_L Z_{index}" for index in range(7)],
        "phase_classes_detected": class_detected,
        "published_profiles": profiles,
        "ranking_counterexample": {
            "old_tied_profiles": ["13_CX_ASAP_depth_7", "13_CX_ASAP_depth_8"],
            "old_total_units": [9, 9],
            "new_flag_blind_units": [3, 6],
            "meaning": "Old scalar-danger ties need not remain ties under the changed readout contract; the two published local proxies differ by a factor of two.",
        },
        "primary_sources": {
            "EXENC": BASE + "work/lanes/EXENC/REPORT.md",
            "ACHECK": BASE + "work/lanes/ACHECK/REPORT.md",
        },
        "source_scope_facts": {
            "EXENC_rank_four_endpoint_subspaces": 11811,
            "EXENC_canonical_CX_counts_exhausted": [11, 12, 13],
            "EXENC_ASAP_circuits": 2987213,
            "EXENC_alternative_schedules": 24202,
            "EXENC_alternative_layerings_exhaustive_max_depth": 6,
            "ACHECK_retained_encoder_paths_screened_at_second_order": 521,
            "ACHECK_diverse_candidates_checked_through_third_order": 33,
            "EXENC_reference_danger_at_p_0_001": 0.0006666666666666669,
            "reference_danger_is_not_global_depth_le_8_minimum": True,
            "counterexample_13_CX_depth_7_and_8_danger": 0.0006,
        },
        "limitations": [
            "The old phase-blind statement concerns A's local Z-basis readout, not acceptance by the entire old circuit.",
            "Profiles are local encoder phase-danger summaries. Correlations, fault timing, all other Pauli components, downstream detectors, and newly added decoder faults still require full-circuit pricing.",
            "No new encoder has been synthesized or shown to improve the final candidate's loss, acceptance, depth, CX count, or judge runtime.",
            "An ideal endpoint subspace alone cannot identify a fault distribution: different paths to the same endpoint require distinct fault-signature summaries.",
            "The old scoring-objective search closure is not an optimality proof for the changed terminal measurement instrument.",
        ],
    }


if __name__ == "__main__":
    result = certify()
    destination = Path(__file__).with_suffix(".json")
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "certificate": str(destination),
        "pair_count": result["pair_count"],
        "detected_pairs": result["detected_pairs"],
        "blind_pairs": result["blind_pairs"],
        "old_units_to_flag_blind_units": {
            row["published_profile"]: [row["old_total_units"], row["new_flag_blind_units"]]
            for row in result["published_profiles"]
        },
    }, indent=2))
