# Constraints, lower bounds and a constructive resource-preparation witness

Reviewed project commit: 7f5a18cf386c850ad8a59e195edb14df087f6457.
Reviewed official judge commit: 76fe47c0324f1c1f8b72a7d55af200e88043b522.

## 1. The strengthened universal floor is sound within its stated scope

Re-executed strengthened.py and independent verify_certificate.py. The latter checked every
one of 2,187 terminal assignments and 64 syndrome sectors (139,968 inequalities), reproducing

    expected conditional L >= 1.36578507905366540835e-5.

The unique minimizer of the relaxed extracted-channel problem is seven helper->output CXs,
with helpers unmeasured after the CX. This is not a realizable preparation circuit or an
attainability certificate. It does not bound an individual finite-shot selected seed-0 score.
Use >=1.3657e-5 if rounding downward; GOAL's literal >=1.366e-5 rounds upward.

Source hashes in the project BOUND/source_hashes.txt match all inspected official source files.
The key semantics are noise.py:31–32,54–88,98–122; check.py:125–128,146–148,253–264,273–302;
exact.py:250–267. The proof covers all syndrome sectors, arbitrary residual logical states,
postselection, allowed logical frames, measurement/reset/first-use cases and shared penultimate
CXs. No flaw was found. The bound is stronger than the earlier 1.1620e-5 floor.

Logical-axis steering alone is negligible in the minimizing tail: vx=.9999813992510169,
vy=.9999639692698678. The optimizing Bloch angle differs from pi/4 by -8.71523e-6 radians,
and improves fixed-|T> loss by only 1.89883e-11. It is not a recommended top-ten candidate.

## 2. Actual overconstraints and incomplete closures

- docs/reference/judge.md:36–37 still calls the final output idle irreducible and asserts every
  output gate costs at least as much. This is too broad: BOUND/PROOF.md:170–194 distinguishes
  universal and measured-partner floors; TERMINAL/REPORT.md:3–6,34–45 closes concrete helpers
  and layouts, not all output endings. A fresh-helper identity insertion is already tested and loses.
- WHOLEEND/BRIEF.md:32–36's optimistic-tail <=2.4e-5 gate is a research target, not a contest rule.
  Its best tested tail 3.3711812301e-5 leaves 3.051657699e-6 below v37d. That difference is only
  a screening budget; postselection makes perfect-resource counterfactuals non-monotonic in general.
- WHOLEEND/MODEL.md:75–90 fixes a sampled last matching and optimizes preceding layers greedily.
  Layerwise OPTIMAL does not prove global optimality; its 104 safe schedules are not exhaustive.
- WHOLEEND/MODEL.md:98–103 fixes every one of 22 individual raw measurement operators, giving
  28 boundary stabilizers. A parity-detector subspace can require fewer boundary stabilizers and
  permit random raw outcomes with affine frames. This can reduce preparation cost. It cannot
  erase the same fixed tail's zero-record harmful faults: best same-tail gain is bounded by
  acceptance renormalization. The 3.37118e-5 tail times .954537 is about 3.21775e-5.
- WHOLEEND/MODEL.md:53–63 and REPORT.md:11–14 say only six minimum-c2 T-only contracts got
  finite-p pricing. Higher-c2 but cheaper resources remain open. A real rank reversal is already
  present in ENDSEARCH/REPORT.md:19–27: the path full grid-free suffix (3.40798e-5) beats ordinary
  square (3.46652e-5), while its ideal round is worse (2.70863e-5 vs 2.55584e-5).
- Official constraints do not require 15T, <=20T, fixed data carriers, three product ancilla
  states, zeroed helpers, zero harmful first-order faults, a 1.5x runtime limit, or full-rank
  intermediate syndrome visibility. Several are reasonable heuristics, but must be scored
  against the actual goal. The real class constraint is xtim's accepted commuting-rotation
  circuit class, and cannot be waived by an evaluator change (problem.md:196–213).

## 3. A new concrete graph / vertex-minor preparation witness

Purpose: synthesize Clifford ancilla resources through local-Clifford graph transformations
and measured helper vertices, instead of restricting to CSS CX elimination or long mobile
stabilizer measurement routes. Start with the square's C block, because both Pauli byproduct
axes are safe to absorb into its readout detector equations.

Constructive result: on a 3x4 grid rectangle missing its upper-left vertex (11 physical cells),
15 nearest-neighbor CXs plus local Cliffords and 4 measured helpers produce Steane |+_L> on
seven cells that have THREE disconnected components in their induced physical grid graph.
The latest exact mapping and affine Pauli masks are in lc_witness.json; it supersedes the first
connected-output probe. The corresponding fragment is lc_c_resource.qasm, not a T-state submission.

Compressed gate counts:

- 11 native X/Z preparations;
- 15 CXs in 4 disjoint matchings;
- 8 output one-qubit Clifford gates;
- 3 extra Sdg gates to implement native Y readout as Sdg followed by native MX;
- 4 readouts, with all 16 measurement branches retained;
- 7 explicitly scheduled native layers under the official folding rules.

Verification: a 2048-amplitude statevector verified every branch, each probability 1/16, and
the maximum fidelity error after the recorded virtual physical Pauli frame was 2.22e-16 for
the compressed circuit. The earlier uncompressed LC construction matched within 2e-15.
No Clifford gates were treated as noiseless. No conditional physical corrections are inserted;
the masks must be incorporated into the later square detectors. The fragment is not validated
against the full official T-state correctness gate because it prepares a C resource, not T.

Why C first: in the square's temporal order D->A || B->C, then B->D || C->A,
an X_C preparation fault becomes X_C X_A only after D->A is over; a Z_C fault is copied to
Z_B by B->C, and Z_B remains on the control during B->D. Thus C-only Pauli faults propagate
only to ancillary readouts, with no D-output Pauli. Wrong preparation-measurement records
also affect detector parities only. This proves isolated C-preparation faults do not directly
cause logical data errors under ideal A/B/D and no preparation contact with other blocks.
It does NOT remove harmful pairs: C faults can hide another prefix/round fault.

What remains: joint placement with D/A/B and prefix cell-release times, full finite-p loss and
acceptance, detector integration, and comparison with ordinary optimized C encoders on the
same endpoints/deadline. This witness establishes geometric and algebraic feasibility only.
It is not a performance winner. Search graph embeddings/local Clifford gauges with the actual
endpoint geometry and fault signatures; do not simply promote this illustrative placement.

## 4. Acceptance-aware resource/tail pricing

See boundary_optimization_note.md for the complete derivation and scope. The central objective
is Tr(E_N rho)/Tr(E_A rho), with both effects pulled back from the actual noisy accepted tail.
For a small justified state subspace it becomes a generalized eigenvalue problem; fixed data
marginals and additional linear constraints give an SDP feasibility test. Start with 1–3 free
gauge qubits. Treat all relaxed-state optima as optimistic, not automatically preparable.

Crucial soundness condition: noiseless correctness belongs to rho_0, not blindly to noisy rho_p.
Fixing an actual preparation channel G_p and its noiseless counterpart G_0 permits one common
gauge input sigma, noisy objective via G_p, and a separate linear correctness constraint via
G_0. A postselection-aware lower-bound certificate is a defensible replacement for arbitrary
tail or c2 cutoffs; a negative relaxation witness only motivates implementation.

Reproduction: python -I bounds_check/strengthened.py; python -I bounds_check/verify_certificate.py;
python bounds_check/lc_disconnected_probe.py; python bounds_check/lc_witness.py.
The graph probes use only Python's standard library; the statevector witness also uses NumPy.
