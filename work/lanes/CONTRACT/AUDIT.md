# Reviewer 18 physical-reduction audit

Verdict: **holds under the inspected STANDARD judge contract**. No counterexample found.
This is a source-to-channel audit, not an assertion that a full circuit attains the bound.
Sources inspected: [BOUND proof](../BOUND/PROOF.md), [judge contract](../../../docs/reference/judge.md),
the primary judge implementation [noise.py](../../../upstream/snu-qff2026-problem/tprep/noise.py), [qasm.py](../../../upstream/snu-qff2026-problem/tprep/qasm.py), [check.py](../../../upstream/snu-qff2026-problem/tprep/check.py), [exact.py](../../../upstream/snu-qff2026-problem/tprep/exact.py), and reviewer 18's [proof](../MAIN/spec/reviewer18/PROOF.txt) and [physical review](../MAIN/spec/reviewer18/PHYSICAL_REVIEW.txt).
Exact arithmetic/dense scripts are rerun only as `python -I` on copies in `reviewer18_copy/`.

| Native case | Independent check and attempted escape |
|---|---|
| Final output read/reset or first-use with only local operations | The raw target has maximally mixed one-site marginals and pure entanglement. A separable output cannot pass raw correctness. Postselection on other qubits cannot entangle a locally reset output. |
| Final output-output CX | Its D2 commutes past disjoint final operations and cannot affect participant records. Retain the whole channel; optimizing all syndrome sectors gives the much larger BOUND exclusion. |
| Earlier last CX, followed by idle | The helper is defined only by a CX at the global last native tick. Earlier partners are not in S. This removes the scheduling ambiguity in the original wording. |
| Penultimate output-output | Final CXs preserve the output components of all Paulis; added helper components disappear on trace. D2 covariance also covers arbitrary final local unitaries. |
| Penultimate output-other-helper | Project 16 two-qubit Paulis onto 8 output Paulis with multiplicity 2; the identity multiplicity includes the dominant I term. Conditional isotropy on the first output covers final non-Clifford gates. |
| Same-axis helper-helper | Projection yields I and three axis products, weights 1-3r,r,r,r. Whole-channel spectral exclusion is essential: individual weight-two errors alone are not a proof for arbitrary incoming syndrome. |
| Opposite-axis helper-helper | The isolated channel has zero optimal loss, so exclusion would be wrong. Reviewer 18 instead factors independent axis flips with a positive correlated residual. The residual must remain in the conditional state. |
| Own output-helper pair | Both CX orientations preserve the pair's D2 by Clifford covariance. Marginalizing the helper yields D1(4p/5) twice; no invalid independent extraction from one pair location is used. |
| Outside partner measured at T in X or Z | Group its post-CX Paulis into commuting/anticommuting branches. The endpoint channels are D1(q0) and completely depolarizing, both admitting D1(2p/5). Readout flips mix positive residual branches and do not undo the factorization. |
| Outside partner not measured at T | A final outside CX cannot also feed a final measurement on its other endpoint at that tick. Arbitrary earlier entanglement with measured systems gives no signaling escape: unitary errors on traced systems disappear under partial trace. |
| Helper with measured outside partner | Project the helper onto its propagated axis before extracting the binary factor. Factoring B(r) from the full D1(q0) before projection would fail; the reviewed proof avoids that step. |
| Penultimate local, idle, or reused measurement | Each supplies D1(p), including the reused measurement's postmeasurement channel. The no-idle-after-final-measurement exception cannot apply to an endpoint used by the final CX. |
| Reset and first use at T-1 or T | Factoring is an identity on the prepared basis state. It does not factor a single-axis flip on an arbitrary entangled state. RX folds before scheduling and uses its own prepared basis. |
| Helper prepared in the commuting basis | The inserted axis flip is an exact invariance of the prepared mixture. Conjugation and tracing imply output dephasing invariance; this cannot secretly prepare a pure entangled output. |
| Logical frames and nonlinear record selection | Common factors hold on each record branch and commute with logical Pauli frames; conditioning on any allowed record predicate preserves them. Ideal decoder records cannot select shots. |
| Coherences between syndrome sectors | The decoded observable and its Pauli-channel adjoints are block diagonal, so sector coherences cannot exceed the maximum certified eigenvalue. |

The scope of the w corollary is the conditional residual **after the exact factorization**, not the raw prefix's syndrome weight. It applies to the all-X assignment; it should not be used as a universal preparation-error budget for other endings.

Geometry does not strengthen this bound: the 242-packing result concerns seven unit squares. The actual contraction uses only the path K-D-H-L, so non-square paths and moving roles remain allowed. Testing this broader geometry is part of the lane's preparation work.

One architectural caution: K/L records check Z_D Z_K and Z_H Z_L. They do **not** measure the third inner stabilizer XXXX, whose image is X_H on an unmeasured helper. Consequently the [[28,1,6]] code distance does not by itself show that all single waiting faults are rejected by this contraction.
