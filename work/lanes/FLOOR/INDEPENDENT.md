# Independent analysis frozen before reviewer 18 / CONTRACT read
Primary sources read: local organizer problem.md, tprep/{noise,qasm,parse,check,exact,grid}.py and tests/test_judge.py. Project judge reference read as orientation, not as proof.

One-layer channel argument: a last-step output must have depolarizing noise. Final M/reset/unused output would leave a separable output, rejected by the raw code-space/target fidelity check. A CX between two outputs has depolarization on that pair. A CX to an unmeasured, discarded helper reduces to D1(4p/5) after tracing its noise. All other outputs have D1(p). Classical frame/acceptance records cannot observe this step's later noise. Thus an operator-norm bound applies conditionally on every earlier record, for every incoming density operator, including entangled ancillas and nonzero syndromes.

Independent enumeration of all 232 unrestricted matchings on seven output labels gives minimum terminal-channel loss 7.4454535276e-6 (arbitrary input) and 7.4454557387e-6 (perfect T_L). A matching with any output-output pair costs at least 3.3758467881e-4. The code enumerates 256 Pauli signatures (six syndrome bits plus physical X/Z parities), then all 64 syndrome/logical 2x2 blocks. The arbitrary-input optimum uses Euclidean norm of X/Y transfer coefficients, not their sum; the perfect T_L input is slightly suboptimal by 2.2e-12.

The one-layer minimum is deliberately too weak to confirm 2.18925128e-5. Any argument for that number needs penultimate noise, including noise on helpers used by final CXs. Idealizing away that penultimate layer produces low prices, saved in counterexamples with their scope. These are counterexamples to a ONE-LAYER bound only; they are not admissible full-circuit counterexamples.

Two-layer independent perfect-prefix tests: inverse CXs with discarded helpers; inverse CX followed by measured helper and output idle; measured helper concurrent with a final CX to a fresh |+> helper; same with helper prepared earlier. The fresh-helper reset carries p orthogonal error; the earlier helper has penultimate idle noise. Both propagate through the final CX and cannot be omitted. Every retained idle straddling the perfect-prefix cut is included by its overlap with the retained tail. The tests use the project all-orders evaluators, and public tprep.check(p=0) verifies raw correctness/class.

Potential loopholes requiring the full audit:
1. Arbitrary incoming syndrome/coherence/entanglement: a best-T_L calculation is insufficient for a universal lower bound.
2. Conditional selection and frames may depend on correlated partner noise; cannot replace a two-qubit noise channel by its unconditional data marginal before selection.
3. A final helper can be reset or measured in the preceding layer, or be fresh at its final CX. Each has different preparation/readout/depolarizing charges.
4. Penultimate measurement/reset on an OUTPUT followed by a final CX: need an entanglement/rank exclusion, not an assumption that all output histories are unitary.
5. Earlier last output event: all later unmeasured steps idle; terminal measurement exemption is legal but output correctness blocks use as final state.
6. Native H-folding across barriers can alter the scheduled depth; proofs must use converted native operations, not QASM line count.
7. Final one-qubit T or arbitrary Clifford: must allow arbitrary local unitary before noise, not only identity/Pauli endings.
8. Measurement records are latest writes, auto frames may differ from declarations, and parity duplicates may have implementation quirks; raw and sampled interpretation must agree.
9. Ideal acceptance may be less than one. A universal conditional bound must survive all such branches, not assume detector-only deterministic selection.
10. Judge correctness tolerance 1e-9 and floating-point certificate rounding: the claim must be an inequality with margin, not equality rounded upward.

Budgets: raw probes finished <2 s; 232 terminal matchings <1 s; ten all-orders perfect-prefix tail cases <10 s. No tom compute used because measured load was 60.86/64; local workers never exceeded two.
