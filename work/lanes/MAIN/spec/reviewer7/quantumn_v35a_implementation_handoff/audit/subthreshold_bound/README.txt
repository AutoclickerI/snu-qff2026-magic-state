QUANTUMN: RE-REVIEW OF THE 1e-5 TARGET
===================================
Audit date: 2026-10-24
User repository examined: AutoclickerI/quantumn
Pinned revision: c5ae3ef5ec2464d79e90886054a39fec9479b7e3
Official judge: SNUQuantums/snu-qff2026-problem
Pinned judge revision: 76fe47c0324f1c1f8b72a7d55af200e88043b522

MAIN RESULT
-----------
Under the inspected STANDARD noise model, p=0.001, and the required retained
seven-qubit Steane output with the judge's actual ideal correction rule, the
accompanying channel/causality argument and exact rational certificate give

    true conditional expected decoded loss 1-F >= 0.00001162.

The relaxed extracted terminal channel has optimal loss
    0.00001162029638920668820439987200204524...

This is a NEW DERIVATION in this review, not an official judge theorem or an
already published result. Its proof is supplied for scrutiny. The arithmetic
certificate verifies the finite-dimensional decoder optimization; the written
proof is needed to justify its reduction from arbitrary admissible circuits.

It does not assert that this bound is tight or that a circuit approaching it
has been constructed. It does not bound every finite-shot Monte Carlo score.
No sub-1e-5 admissible circuit was found or claimed.

WHY A LOWER NUMBER APPEARS
-------------------------
If all preceding noise is omitted and only the marginals of seven final CX
gates to discarded helpers remain, each data qubit has D1(4p/5). Its optimal
decoded loss over arbitrary input is 0.00000744545352762686..., below 1e-5.

That is a relaxation, not a full-circuit witness. In the actual model, an
output ending in CX also has a preceding gate/idle/measurement/reset or
first-use preparation noise source. Each such source allows extraction of
independent D1(p/5). Even a shared preceding CX admits a positive two-sided
factorization. After the final helpers are discarded, the two factors compose
to D1(p-16p^2/75). The proof covers conditioning on all permitted records,
logical Pauli frames, mixed final operations, and arbitrary pre-tail states.

A final output-output CX is considered separately and has a much larger
unavoidable loss, at least 0.0003333. Final measurements/resets without later
re-entanglement fail exact noiseless target correctness.

FILES AND REPRODUCTION
----------------------
PROOF.txt                       Complete channel/causality argument.
terminal_bound.py               Standard-library-only rational verifier.
terminal_bound.json             Exact fractions and high-precision results.
additional_certificates.json    All 21 data-pair checks and reset identity.
independent_matrix.py           Separate 128x128 observable/eigenvalue check.
independent_matrix.json         Its results (NumPy, floating point).
SOURCE_MANIFEST.json            Source pins and SHA-256 fingerprints.

From the extracted directory:
    python3 terminal_bound.py

This regenerates terminal_bound.json and additional_certificates.json. It
enumerates all 4^7 terminal Pauli patterns and all 64 starting syndrome
sectors, checks all 21 final data-data CX pairs, checks reset factorization,
and verifies the rounded-down bound with exact rational comparisons.

Optional independent calculation, if NumPy is installed:
    OPENBLAS_NUM_THREADS=1 python3 independent_matrix.py

This constructs the decoder observable directly from the actual six
stabilizers and scoring signs. It does not import the rational verifier or
use its syndrome-distribution implementation. Agreement in this audit was
3.63e-16 in absolute loss, comfortably below the 2.96e-10 rounding margin of
the exact 1.162e-5 certificate.

SOURCE LOCATIONS
----------------
Judge noise model and native schedule:
https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/noise.py
Judge final decoder, conditional fidelity, and Monte Carlo score:
https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/check.py
Judge stabilizer supports and format:
https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/grid.py
Judge exact noiseless correctness:
https://github.com/SNUQuantums/snu-qff2026-problem/blob/76fe47c0324f1c1f8b72a7d55af200e88043b522/tprep/exact.py
Repository's earlier architecture-specific calculation:
https://github.com/AutoclickerI/quantumn/blob/c5ae3ef5ec2464d79e90886054a39fec9479b7e3/work/bounds.py
Repository findings (including earlier conflicting bound claims):
https://github.com/AutoclickerI/quantumn/blob/c5ae3ef5ec2464d79e90886054a39fec9479b7e3/docs/FINDINGS.md

INTERPRETING PUBLISHED SUB-THRESHOLD RESULTS
-----------------------------------------
Gao, Yuan and Yao, arXiv:2609.12698, explicitly distinguish destructive
postselected error detection from retained-output fidelity. Their quoted
2.19e-7 certificate at p=.001 uses no idle errors and ideal destructive
final Steane tomography with syndrome postselection. It is not a
construction evaluated by this judge's retained-output correction metric.
See sections V.1 and VI: https://arxiv.org/html/2609.12698

This paper is one concrete explanation for apparently incompatible numbers;
the user did not identify the specific source of their sub-1e-5 statement.

RECOMMENDATION
--------------
Audit any sub-1e-5 claim against the exact noise convention, retained output,
acceptance event, and final decoder. A weaker lower bound below 1e-5 does not
prove attainability; an upper bound from a valid circuit would. Under the
inspected rules, improving preparation or helper verification may still
improve current circuits substantially, but does not evade this terminal
obstruction. Neither the old repository figure nor this new lower bound is
an attained optimum.
