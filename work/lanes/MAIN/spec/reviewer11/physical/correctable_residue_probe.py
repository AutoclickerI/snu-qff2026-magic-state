"""Finite certificate for the current BFLAG X-residue contract.

This proves only decoder correctability in an otherwise ideal Steane suffix.
It does not imply a finite-noise advantage, and older relaxed-residue physical
builds already lost; a new candidate must price all cross-region fault pairs.
Uses only the Python standard library.
"""
from pathlib import Path
from collections import defaultdict
import json

HERE = Path(__file__).resolve().parent
ROWS = [[0, 2, 4, 6], [1, 2, 5, 6], [3, 4, 5, 6]]
GENERATORS = [sum(1 << i for i in row) for row in ROWS]
STABILIZERS = {0}
for generator in GENERATORS:
    STABILIZERS |= {x ^ generator for x in list(STABILIZERS)}


def signature(error):
    syndrome = sum(((error & g).bit_count() & 1) << j for j, g in enumerate(GENERATORS))
    return syndrome | ((error.bit_count() & 1) << 3)


def dangerous(s):
    return bool(s & 8) == (not bool(s & 7))


def relaxed_clauses_accept(s):
    bits = [bool(s >> k & 1) for k in range(4)]
    # With active source and all diff/flag bits zero, CP-SAT clauses are:
    # (~parity | s0 | s1 | s2) AND each (~si | parity).
    return ((not bits[3]) or any(bits[:3])) and all((not b) or bits[3] for b in bits[:3])


rows = []
classes = defaultdict(list)
for error in range(128):
    s = signature(error)
    syndrome = s & 7
    correction = (1 << (syndrome - 1)) if syndrome else 0
    corrected = error ^ correction
    decoder_safe = corrected in STABILIZERS
    assert decoder_safe == (not dangerous(s))
    assert decoder_safe == relaxed_clauses_accept(s)
    assert (s == 0) == (error in STABILIZERS)
    classes[s].append(error)
    rows.append(dict(error_mask=error, error_weight=error.bit_count(), signature=s,
                     syndrome=syndrome, parity=s >> 3, decoder_correction=correction,
                     corrected_mask=corrected, decoder_safe=decoder_safe,
                     accepted_by_current_F1=(s == 0)))

safe = [s for s in range(16) if not dangerous(s)]
assert safe == [0, 9, 10, 11, 12, 13, 14, 15]
assert all(len(v) == 8 for v in classes.values())
certificate = {
    'source_pin': '0ff9423a8e69c13998ab1baf7bf09c8e97558a60',
    'scope': 'Exact 128-X-pattern Steane decoder truth certificate; not a noisy-performance certificate.',
    'x_stabilizer_generators': GENERATORS,
    'x_stabilizer_span': sorted(STABILIZERS),
    'safe_signatures': safe,
    'current_F1_safe_classes': [0],
    'current_F1_accepted_patterns': 8,
    'decoder_safe_patterns': 64,
    'patterns_per_signature': {str(s): len(classes[s]) for s in range(16)},
    'safe_predicate': 'parity == OR(syndrome_bit_0, syndrome_bit_1, syndrome_bit_2)',
    'cp_sat_replacement': [
        "m.AddBoolOr(dif + [lit.Not(), s[3].Not(), s[0], s[1], s[2]])",
        "for k in range(3): m.AddBoolOr(dif + [lit.Not(), s[k].Not(), s[3]])",
    ],
    'historical_scope': 'FRESH old v23/R45 relaxed-residue builds scored 8.86e-5 to 1.05e-4; this certificate does not reopen those as successes.',
    'required_new_objective': 'Charge X2leak and full-prefix/suffix cross terms; lns3 X2+KZ*RZ+KA*acc1 alone is invalid for ranking variable accepted residue.',
    'truth_table': rows,
}
(HERE / 'correctable_residue_certificate.json').write_text(json.dumps(certificate, indent=2) + '\n')
print(json.dumps({k: v for k, v in certificate.items() if k not in ('truth_table', 'cp_sat_replacement')}, indent=2))
